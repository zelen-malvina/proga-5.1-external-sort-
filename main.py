import window, threading, os, time, fnmatch
from tkinter import *
from external_sort import generator, external_sort


def label_output(message):
    window.label.config(state="normal")
    window.label.insert('end', f"{message}")
    window.label.see('end')
    window.root.update_idletasks()
    window.label.config(state="disabled")

def async_check_file_size(event, filename): #функция проверки размера файла, помещается в отдельный поток
    while not event.is_set():
        time.sleep(5)
        size = os.path.getsize(filename) // (1024 * 1024)
        window.root.after(0, label_output, f"Размер файла: {size} mb\n")

def async_file_generation(): #функция генерации файла в отдельном потоке
    filename = "file.csv"
    window.btn1.config(state="disabled")
    window.btn2.config(state="disabled")
    window.btn3.config(state="disabled")
    check_event = threading.Event() #событие для остановки проверки размера файла
    check_thread = threading.Thread(target=async_check_file_size, args=(check_event, filename), daemon=True)
    check_thread.start()
    label_output("Генерирую...\n")

    def gen_file():
        try:
            generator.generate_file(filename)
            window.root.after(0, label_output, "Сгенерировал :D\n")
        finally:
            window.root.after(0, lambda: window.btn1.config(state="normal"))
            window.root.after(0, lambda: window.btn2.config(state="normal"))
            window.root.after(0, lambda: window.btn3.config(state="normal"))
            check_event.set()

    gen_thread = threading.Thread(target=gen_file, daemon=True)
    gen_thread.start()

def async_check_files_count(event):
    while not event.is_set():
        count = 0
        time.sleep(5)
        for file in os.listdir("."):
            count += fnmatch.fnmatch(file, "sorted_chunk_*.csv")
        window.root.after(0, label_output, f"Текущее количество чанков: {count}\n")

def async_file_sort():

    if window.combobox.get():
        key = window.fields.index(window.combobox.get())
        first_phase_check_event = threading.Event()
        first_phase_check_thread = threading.Thread(target=async_check_files_count, args=first_phase_check_event, daemon=True)
        first_phase_check_thread.start()
        second_phase_check_event = threading.Event()  # событие для остановки проверки размера файла
        second_phase_check_thread = threading.Thread(target=async_check_file_size, args=(second_phase_check_event, "sorted.txt"), daemon=True)
        window.btn1.config(state="disabled")
        window.btn2.config(state="disabled")
        window.btn3.config(state="disabled")

        def ext_sort():
            try:
                count = external_sort.first_phase(key)
                window.root.after(0, label_output, "Фаза разбиения завершена\n")
                first_phase_check_event.set()
                second_phase_check_thread.start()
                external_sort.merge_phase(key, count)
                window.root.after(0, label_output, "Фаза cлияния завершена\n")

            except Exception as e:
                label_output(f"ошибка: {e}\n")

            finally:
                window.root.after(0, lambda: window.btn1.config(state="normal"))
                window.root.after(0, lambda: window.btn2.config(state="normal"))
                window.root.after(0, lambda: window.btn3.config(state="normal"))
                second_phase_check_event.set()

        sort_thread = threading.Thread(target=ext_sort, daemon=True)
        sort_thread.start()

    else:
        label_output("Выберите поле по которому будет проводиться сортировка\n")

def async_values_output():
    pass


def clear():
    window.label.config(state="normal")
    window.label.delete('1.0', END)
    window.label.config(state="disabled")

window.clear_btn["command"] = clear
window.btn1["command"] = async_file_generation
window.btn2["command"] = async_file_sort
window.root.bind('<Return>', lambda event: window.submit_btn.invoke())
if os.path.exists("file.csv"):
    window.btn2.config(state="normal")
if os.path.exists("sorted.txt"):
    window.btn3.config(state="normal")
window.root.mainloop()

