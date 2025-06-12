# controller.py

import threading
import concurrent.futures
from tkinter import filedialog, messagebox, StringVar
from pathlib import Path

# Импортируем только то, что нужно контроллеру
import processor

class AppController:
    def __init__(self, root, view):
        self.root = root
        self.view = view
        
        # Переменные состояния
        self.folder_path_var = StringVar()
        self.output_folder_var = StringVar()
        self.speed_factor_var = StringVar(value="2.0")
        self.status_var = StringVar(value="Готов к работе")
        self.total_files_to_process = 0

        # Связываем переменные с виджетами представления
        self.view.speed_entry.config(textvariable=self.speed_factor_var)
        self.view.status_label.config(textvariable=self.status_var)

        # Назначаем команды кнопкам из представления
        self.view.in_btn.config(command=self.select_input_folder)
        self.view.out_btn.config(command=self.select_output_folder)
        self.view.process_button.config(command=self.start_processing_thread)

    def select_input_folder(self):
        path = filedialog.askdirectory(title="Выберите папку с аудиофайлами")
        if not path: return
        
        path_obj = Path(path)
        self.folder_path_var.set(path)
        self.view.in_path_label.config(text=f".../{path_obj.name}")

        if not self.output_folder_var.get():
            default_output = path_obj.parent / f"Speedy_{path_obj.name}"
            self.output_folder_var.set(str(default_output))
            self.view.out_path_label.config(text=f".../{default_output.name}")

    def select_output_folder(self):
        path = filedialog.askdirectory(title="Выберите папку для сохранения")
        if path:
            self.output_folder_var.set(path)
            self.view.out_path_label.config(text=f".../{Path(path).name}")

    def start_processing_thread(self):
        if not all([self.folder_path_var.get(), self.output_folder_var.get()]):
            messagebox.showerror("Ошибка", "Пожалуйста, выберите обе папки.")
            return
        try:
            speed = float(self.speed_factor_var.get())
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат скорости.")
            return
        
        self.view.process_button.config(state="disabled")
        self.view.update_progress_wave(0)
        self.status_var.set("Подготовка...")

        thread = threading.Thread(
            target=self._run_processing_logic,
            args=(self.folder_path_var.get(), self.output_folder_var.get(), speed),
            daemon=True
        )
        thread.start()

    def _run_processing_logic(self, in_path, out_path, speed):
        input_path = Path(in_path)
        output_path = Path(out_path)
        
        try:
            all_files = processor.collect_files_to_process(input_path)
            if not all_files:
                self.root.after(0, lambda: messagebox.showinfo("Информация", "Аудиофайлы не найдены."))
                return

            output_path.mkdir(parents=True, exist_ok=True)
            self.total_files_to_process = len(all_files)
            errors = []

            with concurrent.futures.ProcessPoolExecutor() as executor:
                futures = {
                    executor.submit(processor.change_audio_speed_core, file, output_path / file.relative_to(input_path), speed): file
                    for file in all_files
                }
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    file = futures[future]
                    self.root.after(0, self.update_status, f"Обработка {i+1}/{self.total_files_to_process}: {file.name}")
                    self.root.after(0, self.update_progress, i + 1)
                    # ... обработка ошибок
            
            self.root.after(0, self.update_status, "Обработка успешно завершена!")
            self.root.after(0, self.update_progress, self.total_files_to_process)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Критическая ошибка", str(e)))
        finally:
            self.root.after(0, lambda: self.view.process_button.config(state="normal"))
            self.root.after(2000, lambda: self.update_progress(0))
            self.root.after(2000, lambda: self.update_status("Готов к работе"))
            
    def update_progress(self, value):
        if self.total_files_to_process > 0:
            percent = (value / self.total_files_to_process) * 100
            self.view.update_progress_wave(percent)

    def update_status(self, text):
        self.status_var.set(text)