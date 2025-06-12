# view.py

import random
from tkinter import font as tkfont
import ttkbootstrap as ttk
from ttkbootstrap.constants import *

class AppView:
    def __init__(self, root):
        self.root = root
        self.root.configure(background='#f0f0f0')

        self._setup_styles()
        self.font_header = tkfont.Font(family="Segoe UI Light", size=14)
        self.font_main = tkfont.Font(family="Segoe UI", size=10, weight="bold")
        self.font_small = tkfont.Font(family="Segoe UI", size=9)

        card_frame = ttk.Frame(self.root, style='Card.TFrame', padding=30)
        card_frame.pack(padx=20, pady=20, fill=BOTH, expand=YES)

        ttk.Label(card_frame, text="AUDIO SPEED CHANGER", style='Header.TLabel', font=self.font_header).pack(pady=(0, 10))
        ttk.Label(card_frame, text="v3.0 SOLID", style='Subheader.TLabel', font=self.font_small).pack(pady=(0, 20))

        # Виджеты, к которым нужен доступ извне
        self.in_btn = ttk.Button(card_frame, text="Выберите папку с аудио", style='Card.TButton')
        self.in_btn.pack(fill=X, pady=5, ipady=4)
        self.in_path_label = ttk.Label(card_frame, text="...", style='Path.TLabel', font=self.font_small)
        self.in_path_label.pack()

        self.out_btn = ttk.Button(card_frame, text="Выберите куда сохранить", style='Card.TButton')
        self.out_btn.pack(fill=X, pady=(15, 5), ipady=4)
        self.out_path_label = ttk.Label(card_frame, text="...", style='Path.TLabel', font=self.font_small)
        self.out_path_label.pack()

        speed_frame = ttk.Frame(card_frame, style='Card.TFrame')
        speed_frame.pack(pady=20, fill=X)
        ttk.Label(speed_frame, text="СКОРОСТЬ:", style='Card.TLabel', font=self.font_main).pack(side=LEFT, padx=(0, 10))
        self.speed_entry = ttk.Entry(speed_frame, style='Card.TEntry', width=5, font=self.font_main)
        self.speed_entry.pack(side=LEFT)

        self.progress_wave_canvas = ttk.Canvas(card_frame, height=50, background='white', highlightthickness=0)
        self.progress_wave_canvas.pack(fill=X, pady=(20, 5))
        self.update_progress_wave(0) # Начальное состояние

        self.status_label = ttk.Label(card_frame, text="Готов к работе", style='Path.TLabel')
        self.status_label.pack()

        self.process_button = ttk.Button(card_frame, text="ИЗМЕНИТЬ СКОРОСТЬ", style='Accent.Card.TButton')
        self.process_button.pack(fill=X, pady=(10, 0), ipady=8)
    
    def _setup_styles(self):
        style = ttk.Style.get_instance()
        style.configure('Card.TFrame', background='white')
        style.configure('Header.TLabel', background='white', foreground='black')
        style.configure('Subheader.TLabel', background='white', foreground='#a0a0a0')
        style.configure('Card.TLabel', background='white', foreground='black')
        style.configure('Path.TLabel', background='white', foreground='#888888')
        style.configure('Card.TEntry', fieldbackground='white', foreground='black', borderwidth=1, bordercolor='#eeeeee')
        style.configure('Card.TButton', background='white', foreground='black', borderwidth=1, relief='solid', bordercolor='#eeeeee', focusthickness=0)
        style.map('Card.TButton', background=[('active', '#f0f0f0')])
        style.configure('Accent.Card.TButton', background='black', foreground='white', borderwidth=0, focusthickness=0)
        style.map('Accent.Card.TButton', background=[('active', '#333333'), ('disabled', '#555555')])

    def update_progress_wave(self, percent):
        canvas = self.progress_wave_canvas
        canvas.delete("all")
        canvas_width = canvas.winfo_width()
        if canvas_width <= 1: canvas_width = 430
        canvas_height = 50
        fill_color, empty_color = 'black', '#e0e0e0'
        bar_width, gap = 3, 2
        fill_until_x = canvas_width * (percent / 100.0)
        x = 10
        while x < canvas_width - 10:
            bar_height = random.randint(10, canvas_height - 10)
            y1, y2 = (canvas_height - bar_height) / 2, (canvas_height + bar_height) / 2
            current_color = fill_color if x < fill_until_x else empty_color
            canvas.create_rectangle(x, y1, x + bar_width, y2, fill=current_color, outline="")
            x += bar_width + gap