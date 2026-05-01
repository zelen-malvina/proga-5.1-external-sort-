import csv
import heapq

chunk_size = 200000
heap_size = 100000
sorted_chunk_size = 100000
filename = "file.csv"

"""
алгоритм в общем виде:
Считывать большой файл -> заносить в массив пока оперативка не займет ~100мб, отсортировать -> записать в новый файл.
Доставать по одному элементу из файлов -> добавлять в кучу -> вытаскивать минимальный, записывать в новый файл.
"""

def process_line(parts):
    if len(parts) >= 5:
        return [parts[1], parts[2], parts[3], float(parts[4]), int(parts[5])]
    return None

def first_phase(key: int, reverse=True):
    with open(filename, "r") as file:
        chunk = []
        reader = csv.reader(file)
        i = 0
        for row in reader:
            if row:
                chunk.append(process_line(row))
            if len(chunk) == chunk_size:
                chunk.sort(key=lambda x: x[key], reverse=reverse)
                with open(f"sorted_chunk_{i}.csv", "w", newline='') as sort_chunk:
                    writer = csv.writer(sort_chunk)
                    writer.writerows(chunk)
                    i += 1
                    chunk = []
        if chunk:
            chunk.sort(key=lambda x: x[key], reverse=reverse)
            with open(f"sorted_chunk_{i}.csv", "w", newline='') as sort_chunk:
                writer = csv.writer(sort_chunk)
                writer.writerows(chunk)
                chunk = []
        return i

def merge_phase(key, count, reverse=True):
    heap = []
    sort_chunk = []
    files = [open(f"sorted_chunk_{i}.csv", 'r') for i in range(count)]
    readers = [csv.reader(f) for f in files]
    if reverse:

        class Reverse:
            """обертка для обратного сравнения любых типов"""

            def __init__(self, value):
                self.value = value

            def __lt__(self, other):
                return self.value > other.value

            def __eq__(self, other):
                return self.value == other.value

            def __repr__(self):
                return repr(self.value)

        for i, f in enumerate(readers): #первое заполнение кучи
            chunk = []
            while len(chunk) < heap_size // count:
                row = process_line(next(f))
                chunk.append((Reverse(row[key]), i, row)) #структура: ключ, номер файла, строка целиком
            heap.extend(chunk)
        heapq.heapify(heap)

        with open("sorted.txt", "w") as sort:
            while heap: #пока в куче что-то есть постоянно сливаем, добавляем
                row = heapq.heappop(heap) #строка помещаемая в итоговый файл
                sort_chunk.append(str(row[2]) + '\n')
                try:
                    next_row = process_line(next(readers[row[1]]))
                    heapq.heappush(heap, (Reverse(next_row[key]), row[1], next_row))
                except StopIteration:
                    pass
                if len(sort_chunk) >= sorted_chunk_size:
                    sort.writelines(sort_chunk)
                    sort_chunk = []
            if sort_chunk:
                sort.writelines(sort_chunk)

    else:
        for i, f in enumerate(readers): #первое заполнение кучи
            chunk = []
            while len(chunk) < heap_size // count:
                row = process_line(next(f))
                chunk.append((row[key], i, row)) #структура: ключ, номер файла, строка целиком
            heap.extend(chunk)
        heapq.heapify(heap)

        with open("sorted.txt", "w") as sort:
            while heap: #пока в куче что-то есть постоянно сливаем, добавляем
                row = heapq.heappop(heap) #строка помещаемая в итоговый файл
                sort_chunk.append(str(row[2]) + '\n')
                try:
                    next_row = process_line(next(readers[row[1]]))
                    heapq.heappush(heap, (next_row[key], row[1], next_row))
                except StopIteration:
                    pass
                if len(sort_chunk) >= sorted_chunk_size:
                    sort.writelines(sort_chunk)
                    sort_chunk = []
            if sort_chunk:
                sort.writelines(sort_chunk)

    for f in files:
        f.close()