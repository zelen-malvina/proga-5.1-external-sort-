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
    time_start = time.time()
    check_thread.start()
    label_output("Генерирую...\n")

    def gen_file():
        try:
            generator.generate_file(filename)
            time_finish = time.time()
            window.root.after(0, label_output, f"Сгенерировал :D, время генерации: {((time_finish - time_start) / 60):.2f} минут\n")
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
        label_output("Начинаю сортировать...\n")
        first_phase_check_event = threading.Event()
        first_phase_check_thread = threading.Thread(target=async_check_files_count, args=(first_phase_check_event, ), daemon=True)
        first_phase_time_start = time.time()
        first_phase_check_thread.start()
        second_phase_check_event = threading.Event()  # событие для остановки проверки размера файла
        second_phase_check_thread = threading.Thread(target=async_check_file_size, args=(second_phase_check_event, "sorted.txt"), daemon=True)
        window.btn1.config(state="disabled")
        window.btn2.config(state="disabled")
        window.btn3.config(state="disabled")

        def ext_sort():
            try:
                count = external_sort.first_phase(key)
                first_phase_time_finish = time.time()
                window.root.after(0, label_output, f"Фаза разбиения завершена, время выполнения: {((first_phase_time_finish - first_phase_time_start) / 60):.2f} минут\nНачинаю фазу слияния...")
                first_phase_check_event.set()
                second_phase_time_start = time.time()
                second_phase_check_thread.start()
                external_sort.merge_phase(key, count)
                second_phase_time_finish = time.time()
                window.root.after(0, label_output, f"Фаза cлияния завершена, время выполнения: {((second_phase_time_finish - second_phase_time_start) / 60):.2f} минут\n")

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
        label_output("Выберите поле по которому будет проводиться сортировка, иначе никак :/\n")

def async_values_output():
    if window.entry.get():
        try:
            start, stop = map(int, window.entry.get().split())

            if stop - start > 0:
                if stop < 34000000:
                    def file_output():
                        with open("sorted.txt") as f:
                            i = 0
                            row = ''
                            out_str = ''
                            while i <= start:
                                row = next(f)
                                i += 1
                            for i1 in range(stop - start):
                                out_str += (row + '\n')
                                row = next(f)
                            window.root.after(0, label_output, out_str)
                    output_thread = threading.Thread(target=file_output, daemon=True)
                    output_thread.start()
                else:
                    label_output("Слишком большие числа, столько строк в файле не содержится :/. Попробуйте ввести другие числа\n")
            else:
                label_output("Конец не может находиться раньше начала или равняться ему :O. Попробуйте ввести другие числа\n")
        except ValueError as e:
            error_msg = str(e)

            if "invalid literal" in error_msg:
                label_output("Буквы и символы пока не научились быть цифрами :(. Попробуйте ввести числа\n")
            elif "too many values" in error_msg:
                label_output("Слишком много чисел(нужно всего 2(две) штуки) >:(. Попробуйте ввести два числа\n")
            elif "not enough values" in error_msg:
                label_output("С одним числом ничего не получится >:(. Попробуйте ввести два числа\n")
            else:
                label_output(f"Непонятная ошибка какая-то, разберись :O. Ошибка: {error_msg}\n")




    else:
        label_output("Введите начальную и конечную позицию, иначе ничего не получится :(\n")


def clear():
    window.label.config(state="normal")
    window.label.delete('1.0', END)
    window.label.config(state="disabled")

window.clear_btn["command"] = clear
window.btn1["command"] = async_file_generation
window.btn2["command"] = async_file_sort
window.btn3["command"] = async_values_output
window.root.bind('<Return>', lambda event: window.submit_btn.invoke())
if os.path.exists("file.csv"):
    window.btn2.config(state="normal")
if os.path.exists("sorted.txt"):
    window.btn3.config(state="normal")
window.root.mainloop()

