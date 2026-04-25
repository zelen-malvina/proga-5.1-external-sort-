import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText

root = tk.Tk()
root.title("Внешняя сортировочка")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

win_width = screen_width // 2
win_height = screen_height // 2

x = (screen_width - win_width) // 2
y = (screen_height - win_height) // 2

root.geometry(f"{win_width}x{win_height}+{x}+{y}")

root.grid_rowconfigure(0, weight=1)
root.grid_rowconfigure(1, weight=0)
root.grid_columnconfigure(0, weight=1)
root.grid_columnconfigure(1, weight=0)

label = ScrolledText(
    root,
    bg='white',
    relief='sunken',
    wrap='word',
)
label.grid(
    row=0, column=0,
    sticky='nsew',
    padx=5, pady=5
)

button_frame = ttk.Frame(root)
button_frame.grid(
    row=0, column=1,
    sticky='n',
    padx=5, pady=5
)

btn1 = ttk.Button(button_frame, text="Сгенерировать файл")
btn1.pack(
    side='top',
    fill='x',
    padx=5, pady=2
)

btn2 = ttk.Button(button_frame, text="Отсротировать файл")
btn2.pack(
    side='top',
    fill='x',
    padx=5, pady=2
)

btn6 = ttk.Button(button_frame, text="Вывести участок файла")
btn6.pack(
    side='top',
    fill='x',
    padx=5, pady=2
)

entry = ttk.Entry(root)
entry.grid(
    row=2, column=0,
    sticky='ew',
    padx=5, pady=5
)

progress_bar = ttk.Progressbar(orient="horizontal", mode="indeterminate")
progress_bar.grid(
    row=1, column=0,
    sticky='ew',
    padx=5, pady=5
)

submit_btn = ttk.Button(root, text="Ввод")
submit_btn.grid(
    row=2, column=1,
    sticky='ew',
    padx=10, pady=10
)

clear_btn = ttk.Button(button_frame, text="Очистить вывод")
clear_btn.pack(
    side='top',
    fill='x',
    padx=5, pady=2
)


