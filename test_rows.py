count = 0
with open("sorted.txt", "r") as f:
    for _ in f:
        count += 1
print(count)