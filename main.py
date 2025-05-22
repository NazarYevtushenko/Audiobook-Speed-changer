import os
import subprocess
import concurrent.futures
from tkinter import Tk, filedialog, messagebox, Label, Button, Entry, StringVar
from tkinter import ttk
import threading # Для запуска обработки в отдельном потоке
from pathlib import Path # Для удобной работы с путями

def construct_atempo_filter(speed_factor):
    """
    Конструирует строку фильтра atempo для ffmpeg.
    Значения > 2.0 или < 0.5 требуют цепочки фильтров.
    ffmpeg atempo filter supports values between 0.5 and 2.0.
    For > 2.0 and < 100.0, we need to chain them.
    For < 0.5 and > 0.01, we also need to chain.
    """
    if speed_factor <= 0:
        raise ValueError("Speed factor must be positive.")

    filters = []
    if speed_factor > 2.0:
        # Ускорение
        temp_factor = speed_factor
        while temp_factor > 2.0:
            if temp_factor / 2.0 > 2.0: # Если после деления на 2 все еще > 2, то применяем atempo=2.0
                 filters.append("atempo=2.0")
                 temp_factor /= 2.0
            else: # Если близко к 2.0, но больше
                 # Чтобы избежать слишком много фильтров типа atempo=1.00001
                 # если очень близко к 2, можно округлить или просто взять 2.0
                 # Например, для 4.1 -> atempo=2.0, atempo=2.05
                 # Для 3.0 -> atempo=2.0, atempo=1.5
                 # Этот вариант попроще: максимально используем 2.0
                 filters.append("atempo=2.0")
                 temp_factor /= 2.0 # Оставшийся фактор будет < 2.0 (но > 1.0)
                 break # Выходим, чтобы добавить оставшийся фактор
        if temp_factor >= 0.5 and temp_factor <= 2.0 and temp_factor != 1.0 : # Добавляем остаток, если он не 1.0
            filters.append(f"atempo={temp_factor:.4f}")

    elif speed_factor < 0.5:
        # Замедление
        temp_factor = speed_factor
        while temp_factor < 0.5:
            filters.append("atempo=0.5")
            temp_factor /= 0.5 # Фактически temp_factor * 2
            if len(filters) > 5: # Ограничение на количество фильтров, чтобы избежать бесконечности
                break
        if temp_factor >= 0.5 and temp_factor <= 2.0 and temp_factor != 1.0:
            filters.append(f"atempo={temp_factor:.4f}")
    elif speed_factor != 1.0: # Для случая 0.5 <= speed_factor <= 2.0 (и не 1.0)
        filters.append(f"atempo={speed_factor:.4f}")

    if not filters: # Если speed_factor = 1.0
        return None # Нет необходимости в фильтре
    return ",".join(filters)


def change_audio_speed_core(input_path, output_path, speed_factor=2.0):
    atempo_filter_str = construct_atempo_filter(speed_factor)
    if atempo_filter_str is None: # Если скорость 1.0, просто копируем (или можно пропустить)
        # Для простоты можно просто скопировать или вернуть информацию о пропуске
        # В данном случае, если фильтр не нужен, ffmpeg не будет вызван,
        # и файл не будет скопирован в выходную директорию, если только это не реализовать отдельно.
        # Либо можно вызвать ffmpeg для копирования без изменений.
        # Проще всего, если фактор 1.0, не обрабатывать файл.
        # Но если нужно, чтобы он все равно попал в output_folder:
        command = [
            "ffmpeg",
            "-i", str(input_path),
            "-c", "copy", # Копируем аудио и видео потоки без перекодирования
            "-y", # Перезаписать выходной файл без запроса
            str(output_path)
        ]
    else:
        command = [
            "ffmpeg",
            "-i", str(input_path),
            "-filter:a", atempo_filter_str,
            "-c:v", "copy", # Копировать видеодорожку, если она есть
            "-y", # Перезаписать выходной файл без запроса
            str(output_path)
        ]
    try:
        # subprocess.run(command, check=True, capture_output=True, text=True) # Скрываем вывод ffmpeg
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        # Возвращаем ошибку, чтобы ее можно было собрать
        return f"Error processing {input_path}:\n{e.stderr.decode('utf-8', errors='ignore')}"
    except FileNotFoundError:
        return "Error: ffmpeg not found. Please ensure ffmpeg is installed and in your system's PATH."
    return None # Успех

def collect_files_to_process(folder_path):
    """Рекурсивно собирает все аудиофайлы."""
    source_folder = Path(folder_path)
    files = []
    for item in source_folder.rglob('*'): # rglob для рекурсивного поиска
        if item.is_file() and item.suffix.lower() in ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac'):
            files.append(item)
    return files

class AudioSpeedChanger:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Audio Speed Changer")

        style = ttk.Style()
        style.theme_use('clam')

        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ... (остальные элементы GUI как у вас, но с ttk и main_frame) ...
        ttk.Label(main_frame, text="Select folder with audio files:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        
        self.folder_path_var = StringVar()
        folder_entry = ttk.Entry(main_frame, textvariable=self.folder_path_var, width=40, state='readonly')
        folder_entry.grid(row=1, column=0, padx=5, pady=5, sticky="ew")
        
        browse_button = ttk.Button(main_frame, text="Browse...", command=self.select_input_folder)
        browse_button.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(main_frame, text="Select output folder (default: 'Speedy_<input_folder_name>'):").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.output_folder_var = StringVar()
        output_folder_entry = ttk.Entry(main_frame, textvariable=self.output_folder_var, width=40, state='readonly')
        output_folder_entry.grid(row=3, column=0, padx=5, pady=5, sticky="ew")
        
        browse_output_button = ttk.Button(main_frame, text="Browse...", command=self.select_output_folder)
        browse_output_button.grid(row=3, column=1, padx=5, pady=5, sticky="w")


        ttk.Label(main_frame, text="Speed factor (e.g., 2.0 for double, 0.5 for half):").grid(row=4, column=0, padx=5, pady=5, sticky="w")
        self.speed_factor_entry = ttk.Entry(main_frame, width=10)
        self.speed_factor_entry.insert(0, "2.0")
        self.speed_factor_entry.grid(row=4, column=1, padx=5, pady=5, sticky="w")

        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode='determinate')
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=5, pady=10, sticky="ew")

        self.process_button = ttk.Button(main_frame, text="Start Processing", command=self.start_processing_thread)
        self.process_button.grid(row=6, column=0, columnspan=2, padx=5, pady=5, sticky="ew")
        
        main_frame.columnconfigure(0, weight=1)


    def select_input_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder with audio files")
        if folder_path:
            self.folder_path_var.set(folder_path)
            # Установить папку вывода по умолчанию, если она еще не выбрана
            if not self.output_folder_var.get():
                base_name = Path(folder_path).name
                default_output = Path(folder_path).parent / f"Speedy_{base_name}"
                self.output_folder_var.set(str(default_output))


    def select_output_folder(self):
        folder_path = filedialog.askdirectory(title="Select output folder")
        if folder_path:
            self.output_folder_var.set(folder_path)

    def start_processing_thread(self):
        input_folder = self.folder_path_var.get()
        if not input_folder:
            messagebox.showerror("Error", "Please select an input folder.")
            return

        output_folder_str = self.output_folder_var.get()
        if not output_folder_str: # Если папка вывода не выбрана, используем значение по умолчанию
            base_name = Path(input_folder).name
            output_folder_str = str(Path(input_folder).parent / f"Speedy_{base_name}")
            self.output_folder_var.set(output_folder_str) # Обновляем поле ввода

        output_folder = Path(output_folder_str)

        try:
            speed_factor = float(self.speed_factor_entry.get())
            if speed_factor <= 0:
                messagebox.showerror("Error", "Speed factor must be a positive number.")
                return
            # Проверка на разумные пределы для atempo, например, от 0.1 до 100
            # (ffmpeg может поддерживать от 0.01 до 10000, но слишком много фильтров - это долго)
            if not (0.1 <= speed_factor <= 100):
                 messagebox.showwarning("Warning", "Speed factors far from 1.0 (e.g., <0.1 or >100) might take very long or fail.")
        except ValueError:
            messagebox.showerror("Error", "Invalid speed factor. Please enter a number.")
            return

        self.process_button.config(state="disabled")
        self.progress_bar['value'] = 0
        
        # Запуск обработки в отдельном потоке
        thread = threading.Thread(target=self.run_processing_logic, 
                                  args=(Path(input_folder), output_folder, speed_factor),
                                  daemon=True)
        thread.start()

    def run_processing_logic(self, input_folder_path, output_folder_path, speed_factor):
        try:
            all_files = collect_files_to_process(input_folder_path)
            if not all_files:
                messagebox.showinfo("Info", "No audio files found in the selected folder or its subfolders.")
                self.root.after(0, lambda: self.process_button.config(state="normal"))
                return

            if not output_folder_path.exists():
                output_folder_path.mkdir(parents=True, exist_ok=True)

            self.progress_bar['maximum'] = len(all_files)
            errors = []

            with concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count()) as executor:
                futures = {}
                for input_file_path in all_files:
                    # Сохраняем относительный путь для создания такой же структуры в папке вывода
                    relative_path = input_file_path.relative_to(input_folder_path)
                    output_file_path = output_folder_path / relative_path
                    
                    # Создаем поддиректории в папке вывода, если они нужны
                    output_file_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Если скорость 1.0, и мы хотим просто скопировать файл
                    if speed_factor == 1.0:
                        # Можно просто скопировать файл с помощью shutil
                        # import shutil
                        # shutil.copy2(input_file_path, output_file_path)
                        # Или пропустить обработку ffmpeg для этого файла
                        # Для примера, будем вызывать ffmpeg с копированием
                        pass # change_audio_speed_core обработает это

                    futures[executor.submit(change_audio_speed_core, input_file_path, output_file_path, speed_factor)] = input_file_path.name
                
                for i, future in enumerate(concurrent.futures.as_completed(futures)):
                    file_name = futures[future]
                    try:
                        result = future.result()
                        if result: # Если есть строка ошибки
                            errors.append(result)
                    except Exception as e:
                        errors.append(f"Error processing file {file_name}: {e}")
                    finally:
                        # Обновление GUI из потока должно быть через root.after
                        self.root.after(0, self.update_progress, i + 1)
            
            # По завершении всех задач
            if errors:
                error_message = "Processing completed with some errors:\n\n" + "\n\n".join(errors)
                # Можно использовать кастомное диалоговое окно для длинных сообщений об ошибках
                print(error_message) # Для отладки, если messagebox не вмещает
                messagebox.showerror("Processing Errors", "Some files could not be processed. See console/log for details if message is too long.")
            else:
                messagebox.showinfo("Success", f"All files have been processed and saved to '{output_folder_path}'.")

        except FileNotFoundError as e: # Например, ffmpeg не найден
             messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("An Unexpected Error Occurred", f"An error occurred: {e}")
        finally:
            self.root.after(0, lambda: self.process_button.config(state="normal"))
            self.root.after(0, self.update_progress, 0) # Сбросить прогресс

    def update_progress(self, value):
        self.progress_bar['value'] = value
        # self.root.update_idletasks() # root.after делает это ненужным явно

if __name__ == "__main__":
    # Проверка наличия ffmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        root_check = Tk()
        root_check.withdraw() # Скрываем основное окно для messagebox
        messagebox.showerror("Error", "ffmpeg not found. Please install ffmpeg and ensure it is in your system's PATH.")
        root_check.destroy()
        exit()

    root = Tk()
    # Устанавливаем минимальный размер и позволяем изменять размер
    root.minsize(450, 250) 
    app = AudioSpeedChanger(root)
    root.mainloop()