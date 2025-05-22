import os
import subprocess
import concurrent.futures
from tkinter import Tk, filedialog, messagebox, Label, Button, Entry, StringVar
from tkinter import ttk

def change_audio_speed(input_path, output_path, speed_factor=2.0):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-filter:a", f"atempo={speed_factor}",
        "-c:v", "copy",
        output_path
    ]
    subprocess.run(command, check=True)

def process_files(folder_path, output_folder, speed_factor, progress_bar, root):
    files_to_process = [
        os.path.join(folder_path, file_name)
        for file_name in os.listdir(folder_path)
        if file_name.lower().endswith(('.mp3', '.wav', '.ogg', '.flac'))
    ]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    total_files = len(files_to_process)
    progress_bar['maximum'] = total_files
    progress_bar['value'] = 0

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for input_path in files_to_process:
            file_name = os.path.basename(input_path)
            output_path = os.path.join(output_folder, file_name)
            futures.append(executor.submit(change_audio_speed, input_path, output_path, speed_factor))

        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred: {e}")
            finally:
                progress_bar['value'] += 1
                root.update_idletasks()

    for dir_name in os.listdir(folder_path):
        dir_path = os.path.join(folder_path, dir_name)
        if os.path.isdir(dir_path):
            new_output_folder = os.path.join(output_folder, dir_name)
            process_files(dir_path, new_output_folder, speed_factor, progress_bar, root)

    messagebox.showinfo("Success", f"Files have been processed and saved to the '{output_folder}' folder.")

class AudioSpeedChanger:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Speed Changer")

        # Set the theme
        style = ttk.Style()
        style.theme_use('clam')

        # Create the main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=("n", "e", "s", "w"))

        # Create the labels and entry
        label = ttk.Label(main_frame, text="Select folder with audio files to speed up:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        speed_factor_label = ttk.Label(main_frame, text="Enter speed factor (e.g., 2.0 for double speed):")
        speed_factor_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        self.speed_factor_entry = ttk.Entry(main_frame, width=10)
        self.speed_factor_entry.insert(0, "2.0")  # Default value
        self.speed_factor_entry.grid(row=1, column=1, padx=5, pady=5, sticky=("e", "w"))

        # Create the progress bar
        self.progress_bar = ttk.Progressbar(main_frame, orient="horizontal", length=300, mode='determinate')
        self.progress_bar.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky=("e", "w"))

        # Create the select folder button
        select_button = ttk.Button(main_frame, text="Select Folder", command=self.select_folder)
        select_button.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky=("e", "w"))

    def select_folder(self):
        folder_path = filedialog.askdirectory(title="Select folder with audio files")
        if not folder_path:
            messagebox.showinfo("Info", "No folder selected.")
            return

        speed_factor = self.speed_factor_entry.get()
        try:
            speed_factor = float(speed_factor)
        except ValueError:
            messagebox.showerror("Error", "Invalid speed factor. Please enter a number.")
            return

        output_folder = os.path.join(os.path.dirname(folder_path), "Speedy_" + os.path.basename(folder_path))
        process_files(folder_path, output_folder, speed_factor, self.progress_bar, self.root)

if __name__ == "__main__":
    root = Tk()
    root.title("Audio Speed Changer")
    root.geometry("400x200")  # Set the initial window size

    app = AudioSpeedChanger(root)
    root.mainloop()