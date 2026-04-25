import window
import threading
import os
import time
from tkinter.messagebox import showerror, showinfo
from tkinter import *
from external_sort import generator, external_sort

def label_output(message):
    window.label.insert('end', f"{message}")
    window.label.see('end')
    #window.root.update_idletasks()

def async_check_file_size(event, filename): #функция проверки размера файла, помещается в отдельный поток
    while not event.is_set():
        time.sleep(5)
        size = os.path.getsize(filename) // (1024 * 1024)
        window.root.after(0, label_output, f"Сгенерировано: {size} mb\n")

def async_file_generation(): #функция генерации файла в отдельном потоке
    filename = "file.csv"
    window.btn1.config(state="disabled")
    '''
    check_event = threading.Event() #событие для остановки проверки размера файла
    checkThread = threading.Thread(target=async_check_file_size, args=(check_event, filename), daemon=True)
    checkThread.start()
    '''
    window.progress_bar.start(10)
    label_output("Генерирую...\n")

    def gen_file():
        try:
            generator.generate_file(filename)
            window.root.after(0, label_output, "Сгенерировал :D\n")
        finally:
            window.root.after(0, lambda: window.progress_bar.stop())
            window.root.after(0, lambda: window.btn1.config(state="normal"))
            #check_event.set()

    genThread = threading.Thread(target=gen_file, daemon=True)
    genThread.start()




def clear():
    window.label.delete('1.0', END)

window.clear_btn["command"] = clear
window.btn1["command"] = async_file_generation
window.root.bind('<Return>', lambda event: window.submit_btn.invoke())
window.root.mainloop()

