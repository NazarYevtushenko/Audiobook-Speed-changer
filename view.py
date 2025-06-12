# view.py

import random
from tkinter import font as tkfont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class AppView:
    def __init__(self, root):
        self.root = root
        
        # Основной цвет фона всего окна
        self.root.configure(background='#0d1a35')

        # ИЗМЕНЕНИЕ: Определяем шрифты ДО настройки стилей, чтобы избежать ошибки
        self.font_header = tkfont.Font(family="Segoe UI Light", size=16)
        self.font_main = tkfont.Font(family="Segoe UI Light", size=11, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI Light", size=9)

        # Загружаем иконки
        self._load_images()

        # Настраиваем кастомные стили
        self._setup_styles()

        # --- Главная "карточка" ---
        card_frame = ttk.Frame(self.root, style='Card.TFrame', padding=30)
        card_frame.pack(padx=20, pady=20, fill=BOTH, expand=YES)
        
        # --- Заголовок ---
        header_frame = ttk.Frame(card_frame, style='Card.TFrame')
        header_frame.pack(pady=(0, 30), fill=X)
        ttk.Label(header_frame, image=self.img_header, style='Icon.TLabel').pack(side=LEFT, padx=(0, 15))
        ttk.Label(header_frame, text="AUDIO SPEED CHANGER", style='Header.TLabel', font=self.font_header).pack(side=LEFT)

        # --- Основные элементы управления ---
        self.in_btn = ttk.Button(card_frame, text="ИСХОДНАЯ ПАПКА", style='Neon.TButton', image=self.img_folder_in, compound=LEFT)
        self.in_btn.pack(fill=X, pady=5, ipady=6)
        self.in_path_label = ttk.Label(card_frame, text="не выбрана", style='Path.TLabel', font=self.font_small)
        self.in_path_label.pack()

        self.out_btn = ttk.Button(card_frame, text="ПАПКА НАЗНАЧЕНИЯ", style='Neon.TButton', image=self.img_folder_out, compound=LEFT)
        self.out_btn.pack(fill=X, pady=(15, 5), ipady=6)
        self.out_path_label = ttk.Label(card_frame, text="не выбрана", style='Path.TLabel', font=self.font_small)
        self.out_path_label.pack()

        speed_frame = ttk.Frame(card_frame, style='Card.TFrame')
        speed_frame.pack(pady=30, fill=X)
        ttk.Label(speed_frame, image=self.img_speed, style='Icon.TLabel').pack(side=LEFT, padx=(0, 15))
        ttk.Label(speed_frame, text="КОЭФФИЦИЕНТ:", style='Neon.TLabel', font=self.font_main).pack(side=LEFT, padx=(0, 10))
        self.speed_entry = ttk.Entry(speed_frame, style='Neon.TEntry', width=5, font=self.font_main)
        self.speed_entry.pack(side=LEFT)

        # --- Прогресс и запуск ---
        self.progress_wave_canvas = ttk.Canvas(card_frame, height=50, background='#192e54', highlightthickness=0)
        self.progress_wave_canvas.pack(fill=X, pady=(20, 5))
        self.update_progress_wave(0)

        self.status_label = ttk.Label(card_frame, text="Готов к работе", style='Path.TLabel')
        self.status_label.pack()

        self.process_button = ttk.Button(card_frame, text="ЗАПУСК", style='Accent.Neon.TButton', image=self.img_play, compound=LEFT)
        self.process_button.pack(fill=X, pady=(15, 0), ipady=8)

    def _load_images(self):
        """Загружает все иконки один раз, чтобы избежать проблем со сборщиком мусора"""
        try:
            self.img_header = ttk.PhotoImage(name='stopwatch', width=24)
            self.img_folder_in = ttk.PhotoImage(name='box-arrow-in-right', width=16)
            self.img_folder_out = ttk.PhotoImage(name='box-arrow-right', width=16)
            self.img_speed = ttk.PhotoImage(name='sliders', width=16)
            self.img_play = ttk.PhotoImage(name='play-fill', width=16)
        except Exception as e:
            print(f"Ошибка загрузки иконок: {e}. Убедитесь, что ttkbootstrap установлен корректно.")
            self.img_header = self.img_folder_in = self.img_folder_out = self.img_speed = self.img_play = None

    def _setup_styles(self):
        """Настройка всех кастомных стилей для неонового дизайна."""
        style = ttk.Style.get_instance()
        
        BG_COLOR = '#0d1a35'
        CARD_COLOR = '#192e54'
        NEON_CYAN = '#00f2ea'
        LIGHT_GREY = '#7b8bab'

        style.configure('.', background=BG_COLOR, foreground=LIGHT_GREY, borderwidth=0, focusthickness=0)
        style.configure('TFrame', background=BG_COLOR)
        
        style.configure('Card.TFrame', background=CARD_COLOR)
        style.configure('Icon.TLabel', background=CARD_COLOR)
        style.configure('Header.TLabel', background=CARD_COLOR, foreground='white')
        style.configure('Path.TLabel', background=CARD_COLOR, foreground=LIGHT_GREY)
        style.configure('Neon.TLabel', background=CARD_COLOR, foreground=NEON_CYAN)

        style.configure('Neon.TButton', 
                        background=CARD_COLOR, 
                        foreground=NEON_CYAN, 
                        bordercolor=NEON_CYAN, 
                        borderwidth=1, 
                        relief='solid',
                        font=self.font_main)
        style.map('Neon.TButton', 
                  background=[('active', BG_COLOR)],
                  bordercolor=[('active', 'white')])

        style.configure('Accent.Neon.TButton', 
                        background=NEON_CYAN, 
                        foreground=BG_COLOR,
                        font=self.font_main)
        style.map('Accent.Neon.TButton',
                  background=[('active', 'white'), ('disabled', LIGHT_GREY)],
                  foreground=[('disabled', CARD_COLOR)])

        style.configure('Neon.TEntry', 
                        fieldbackground=BG_COLOR, 
                        foreground=NEON_CYAN, 
                        bordercolor=NEON_CYAN, 
                        borderwidth=1,
                        insertcolor=NEON_CYAN)

    def update_progress_wave(self, percent):
        canvas = self.progress_wave_canvas
        canvas.delete("all")
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1: canvas_width = 430
        canvas_height = 50
        
        fill_color = '#00f2ea'
        empty_color = '#2a4a85'
        
        bar_width, gap = 3, 2
        fill_until_x = canvas_width * (percent / 100.0)
        
        x = 10
        while x < canvas_width - 10:
            bar_height = random.randint(5, canvas_height - 10)
            y1, y2 = (canvas_height - bar_height) / 2, (canvas_height + bar_height) / 2
            current_color = fill_color if x < fill_until_x else empty_color
            canvas.create_rectangle(x, y1, x + bar_width, y2, fill=current_color, outline="")
            x += bar_width + gap