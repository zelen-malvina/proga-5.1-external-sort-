#ifndef CORE_HPP
#define CORE_HPP

#include <string>
#include <vector>

#ifdef _WIN32
    #define DLL_EXPORT __declspec(dllexport)
#else
    #define DLL_EXPORT
#endif

struct Row {
    std::string col0;
    std::string col1;
    std::string col2;
    double col3;
    int col4;

    std::string to_python_str() const;
};

extern "C" {
    DLL_EXPORT int first_phase(int key, bool reverse);
    DLL_EXPORT void merge_phase(int key, int count, bool reverse);
}

#endif
