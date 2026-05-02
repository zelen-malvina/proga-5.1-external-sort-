#include "main.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <algorithm>
#include <filesystem>
#include <queue>
#include <iomanip>

namespace fs = std::filesystem;

const int chunk_size = 200000;
const int heap_size = 100000;
const int sorted_chunk_size = 100000;
const std::string filename = "file.csv";

std::string Row::to_python_str() const {
    std::stringstream ss;
    ss << "['" << col0 << "', '" << col1 << "', '" << col2 << "', "
       << std::fixed << std::setprecision(1) << col3 << ", " << col4 << "]";
    return ss.str();
}

// Безопасная очистка строки от символов переноса
void trim_row(std::string& s) {
    s.erase(std::remove(s.begin(), s.end(), '\r'), s.end());
    s.erase(std::remove(s.begin(), s.end(), '\n'), s.end());
}

bool process_line(const std::string& line, Row& row) {
    if (line.empty()) return false;
    std::vector<std::string> parts;
    std::stringstream ss(line);
    std::string part;
    while (std::getline(ss, part, ',')) {
        parts.push_back(part);
    }
    if (parts.size() >= 5) {
        row.col0 = parts[0];
        row.col1 = parts[1];
        row.col2 = parts[2];
        try {
            row.col3 = std::stod(parts[3]);
            row.col4 = std::stoi(parts[4]);
        } catch (...) {
            return false;
        }
        return true;
    }
    return false;
}

// Универсальный компаратор
bool compareRows(const Row& a, const Row& b, int key, bool reverse) {
    bool result = false;
    if (key == 0) result = a.col0 < b.col0;
    else if (key == 1) result = a.col1 < b.col1;
    else if (key == 2) result = a.col2 < b.col2;
    else if (key == 3) result = a.col3 < b.col3;
    else if (key == 4) result = a.col4 < b.col4;

    if (reverse) {
        // Для reverse=True (сортировка по убыванию)
        // В std::sort: a > b. В priority_queue: имитируем макс-кучу.
        bool greater = false;
        if (key == 0) greater = b.col0 < a.col0;
        else if (key == 1) greater = b.col1 < a.col1;
        else if (key == 2) greater = b.col2 < a.col2;
        else if (key == 3) greater = b.col3 < a.col3;
        else if (key == 4) greater = b.col4 < a.col4;
        return greater;
    }
    return result;
}

struct HeapNode {
    Row row;
    int file_index;
    int key;
    bool reverse;

    // В priority_queue оператор < определяет, что элемент уйдет вниз.
    // Нам нужно, чтобы при reverse=False наверху был минимальный (мин-куча),
    // а при reverse=True — максимальный (макс-куча).
    bool operator<(const HeapNode& other) const {
        if (reverse) {
            // Макс-куча: текущий "меньше" другого, если реально меньше
            return compareRows(this->row, other.row, key, false);
        } else {
            // Мин-куча: текущий "меньше" другого, если реально больше
            return compareRows(other.row, this->row, key, false);
        }
    }
};

extern "C" DLL_EXPORT int first_phase(int key, bool reverse) {
    try {
        std::ifstream file(filename);
        if (!file.is_open()) return 0;

        std::string line;
        std::vector<Row> chunk;
        int i = 0;
        if (!fs::exists("sorted_chunks")) fs::create_directory("sorted_chunks");

        while (std::getline(file, line)) {
            Row row;
            if (process_line(line, row)) {
                chunk.push_back(row);
            }
            if (chunk.size() >= chunk_size) {
                std::sort(chunk.begin(), chunk.end(), [&](const Row& a, const Row& b) {
                    return compareRows(a, b, key, reverse);
                });
                std::ofstream out("sorted_chunks/sorted_chunk_" + std::to_string(i++) + ".csv");
                for (const auto& r : chunk)
                    out << r.col0 << "," << r.col1 << "," << r.col2 << "," << r.col3 << "," << r.col4 << "\n";
                chunk.clear();
            }
        }
        if (!chunk.empty()) {
            std::sort(chunk.begin(), chunk.end(), [&](const Row& a, const Row& b) {
                return compareRows(a, b, key, reverse);
            });
            std::ofstream out("sorted_chunks/sorted_chunk_" + std::to_string(i++) + ".csv");
            for (const auto& r : chunk)
                out << r.col0 << "," << r.col1 << "," << r.col2 << "," << r.col3 << "," << r.col4 << "\n";
        }
        return i;
    } catch (...) { return -1; }
}

extern "C" DLL_EXPORT void merge_phase(int key, int count, bool reverse) {
    try {
        std::priority_queue<HeapNode> heap;
        std::vector<std::ifstream> files(count);
        std::vector<Row> sort_chunk;
        std::ofstream out_file("sorted.txt");

        for (int i = 0; i < count; ++i) {
            files[i].open("sorted_chunks/sorted_chunk_" + std::to_string(i) + ".csv");
            std::string line;
            int lines_to_read = heap_size / (count > 0 ? count : 1);
            while (lines_to_read-- > 0 && std::getline(files[i], line)) {
                Row row;
                if (process_line(line, row)) {
                    heap.push({row, i, key, reverse});
                }
            }
        }

        while (!heap.empty()) {
            HeapNode top = heap.top();
            heap.pop();
            sort_chunk.push_back(top.row);

            std::string line;
            if (std::getline(files[top.file_index], line)) {
                Row next_row;
                if (process_line(line, next_row)) {
                    heap.push({next_row, top.file_index, key, reverse});
                }
            }

            if (sort_chunk.size() >= sorted_chunk_size) {
                for (const auto& r : sort_chunk) out_file << r.to_python_str() << "\n";
                sort_chunk.clear();
            }
        }

        for (const auto& r : sort_chunk) out_file << r.to_python_str() << "\n";
        out_file.close();

        for (int i = 0; i < count; ++i) {
            files[i].close();
            fs::remove("sorted_chunks/sorted_chunk_" + std::to_string(i) + ".csv");
        }
        fs::remove_all("sorted_chunks");
    } catch (...) { }
}
