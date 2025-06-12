# processor.py

import subprocess
from pathlib import Path

def construct_atempo_filter(speed_factor):
    """Конструирует строку фильтра atempo для ffmpeg."""
    if speed_factor <= 0:
        raise ValueError("Speed factor must be positive.")
    filters = []
    if speed_factor > 2.0:
        temp_factor = speed_factor
        while temp_factor > 2.0:
            filters.append("atempo=2.0")
            temp_factor /= 2.0
        if temp_factor >= 0.5 and temp_factor <= 2.0 and temp_factor != 1.0:
            filters.append(f"atempo={temp_factor:.4f}")
    elif speed_factor < 0.5:
        temp_factor = speed_factor
        while temp_factor < 0.5:
            filters.append("atempo=0.5")
            temp_factor /= 0.5
            if len(filters) > 5: break
        if temp_factor >= 0.5 and temp_factor <= 2.0 and temp_factor != 1.0:
            filters.append(f"atempo={temp_factor:.4f}")
    elif speed_factor != 1.0:
        filters.append(f"atempo={speed_factor:.4f}")
    if not filters:
        return None
    return ",".join(filters)

def change_audio_speed_core(input_path, output_path, speed_factor=2.0):
    """Основная функция обработки одного файла с помощью FFmpeg."""
    try:
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
    except ImportError:
        ffmpeg_path = "ffmpeg"

    atempo_filter_str = construct_atempo_filter(speed_factor)
    if atempo_filter_str is None:
        command = [ffmpeg_path, "-i", str(input_path), "-c", "copy", "-y", str(output_path)]
    else:
        command = [ffmpeg_path, "-i", str(input_path), "-filter:a", atempo_filter_str, "-c:v", "copy", "-y", str(output_path)]
    try:
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, creationflags=subprocess.CREATE_NO_WINDOW)
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, command, output=stdout, stderr=stderr)
    except subprocess.CalledProcessError as e:
        return f"Error processing {input_path}:\n{e.stderr}"
    except FileNotFoundError:
        return "Error: ffmpeg not found."
    return None

def collect_files_to_process(folder_path):
    """Рекурсивно собирает все поддерживаемые аудиофайлы из папки."""
    source_folder = Path(folder_path)
    files = []
    supported_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac')
    for item in source_folder.rglob('*'):
        if item.is_file() and item.suffix.lower() in supported_extensions:
            files.append(item)
    return files