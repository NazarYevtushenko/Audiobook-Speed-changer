# main.py

import ttkbootstrap as ttk
from view import AppView
from controller import AppController

if __name__ == "__main__":
    # 1. Создаем главное окно
    root = ttk.Window(themename="litera", size=(500, 650), title="Audio Speed Changer")
    
    # 2. Создаем экземпляр Представления
    view = AppView(root)
    
    # 3. Создаем экземпляр Контроллера, связывая его с Представлением
    controller = AppController(root, view)
    
    # 4. Запускаем главный цикл приложения
    root.mainloop()