import time
import threading
import random
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode, Key
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog

class AdvancedAutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.clicking = False
        self.running = True
        
        # Настройки
        self.click_points = []  # Список точек [(x1, y1), (x2, y2), ...]
        self.current_point_index = 0
        self.delay = 0.1  # Задержка между кликами (сек)
        self.delay_variation = 0.02  # Случайная вариация
        self.cycle_delay = 0.0  # Задержка между циклами (сек)
        self.cycles = 1  # Количество циклов
        self.current_cycle = 0
        self.click_count = 0
        self.total_clicks = 0
        
        # Горячие клавиши
        self.toggle_key = KeyCode(char='v')  # V - старт/стоп
        self.exit_key = KeyCode(char='b')    # B - выход
        self.add_point_key = KeyCode(char='a')  # A - добавить точку
        self.clear_points_key = KeyCode(char='c')  # C - очистить точки
        
    def get_random_delay(self):
        """Случайная задержка для анти-детекта"""
        return max(0.001, self.delay + random.uniform(-self.delay_variation, self.delay_variation))
    
    def click_loop(self):
        """Основной цикл кликов"""
        while self.clicking and self.running:
            # Проверяем, есть ли точки
            if not self.click_points:
                # Если точек нет, кликаем по текущей позиции
                self.mouse.click(Button.left)
                self.click_count += 1
                self.total_clicks += 1
                time.sleep(self.get_random_delay())
            else:
                # Кликаем по точкам по очереди
                x, y = self.click_points[self.current_point_index]
                self.mouse.position = (x, y)
                time.sleep(0.05)  # Небольшая задержка перед кликом
                self.mouse.click(Button.left)
                
                self.click_count += 1
                self.total_clicks += 1
                
                # Переходим к следующей точке
                self.current_point_index += 1
                
                # Если дошли до конца списка точек
                if self.current_point_index >= len(self.click_points):
                    self.current_point_index = 0
                    self.current_cycle += 1
                    
                    # Если все циклы завершены
                    if self.current_cycle >= self.cycles:
                        self.clicking = False
                        print(f"✅ Все {self.cycles} циклов завершены!")
                        break
                    else:
                        # ️ ЗАДЕРЖКА МЕЖДУ ЦИКЛАМИ
                        if self.cycle_delay > 0:
                            time.sleep(self.cycle_delay)
                
                time.sleep(self.get_random_delay())
    
    def start(self):
        if not self.clicking:
            self.clicking = True
            self.click_count = 0
            self.current_cycle = 0
            self.current_point_index = 0
            thread = threading.Thread(target=self.click_loop, daemon=True)
            thread.start()
            return True
        return False
    
    def stop(self):
        if self.clicking:
            self.clicking = False
            return True
        return False
    
    def add_point(self):
        """Добавить текущую позицию мыши"""
        x, y = self.mouse.position
        self.click_points.append((x, y))
        print(f"📍 Точка добавлена: ({x}, {y}) - Всего точек: {len(self.click_points)}")
        return x, y
    
    def clear_points(self):
        """Очистить все точки"""
        self.click_points.clear()
        self.current_point_index = 0
        print("️ Все точки очищены")
    
    def on_press(self, key):
        """Обработка клавиш"""
        if key == self.toggle_key:
            if self.clicking:
                self.stop()
            else:
                self.start()
        elif key == self.exit_key:
            self.running = False
            self.clicking = False
            exit()
        elif key == self.add_point_key:
            self.add_point()
        elif key == self.clear_points_key:
            self.clear_points()

class AdvancedClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 Advanced AutoClicker")
        self.root.geometry("500x650")
        self.root.resizable(False, False)
        self.root.configure(bg='#1e1e1e')
        
        self.autoclicker = AdvancedAutoClicker()
        
        # Стили
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabel', background='#1e1e1e', foreground='white', font=('Arial', 10))
        style.configure('TButton', font=('Arial', 10))
        
        # Заголовок
        title = tk.Label(root, text="🎮 Advanced AutoClicker", 
                        font=("Arial", 18, "bold"), bg='#1e1e1e', fg='#00ff00')
        title.pack(pady=10)
        
        # Настройки времени
        time_frame = tk.LabelFrame(root, text="⏱️ Настройки времени", 
                                   font=("Arial", 12, "bold"), bg='#2d2d2d', fg='white')
        time_frame.pack(pady=10, padx=10, fill='x')
        
        # Задержка
        delay_frame = tk.Frame(time_frame, bg='#2d2d2d')
        delay_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(delay_frame, text="Задержка (сек):", bg='#2d2d2d', fg='white').pack(side=tk.LEFT)
        self.delay_var = tk.DoubleVar(value=0.1)
        delay_spinbox = tk.Spinbox(delay_frame, from_=0.001, to=10, increment=0.01, 
                                   textvariable=self.delay_var, width=10)
        delay_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Вариация
        var_frame = tk.Frame(time_frame, bg='#2d2d2d')
        var_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(var_frame, text="Вариация (сек):", bg='#2d2d2d', fg='white').pack(side=tk.LEFT)
        self.var_var = tk.DoubleVar(value=0.02)
        var_spinbox = tk.Spinbox(var_frame, from_=0, to=1, increment=0.01, 
                                 textvariable=self.var_var, width=10)
        var_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Настройки циклов
        cycle_frame = tk.LabelFrame(root, text=" Настройки циклов", 
                                    font=("Arial", 12, "bold"), bg='#2d2d2d', fg='white')
        cycle_frame.pack(pady=10, padx=10, fill='x')
        
        cycles_frame = tk.Frame(cycle_frame, bg='#2d2d2d')
        cycles_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(cycles_frame, text="Количество циклов:", bg='#2d2d2d', fg='white').pack(side=tk.LEFT)
        self.cycles_var = tk.IntVar(value=1)
        cycles_spinbox = tk.Spinbox(cycles_frame, from_=1, to=9999, increment=1, 
                                    textvariable=self.cycles_var, width=10)
        cycles_spinbox.pack(side=tk.RIGHT, padx=5)

        #  ЗАДЕРЖКА МЕЖДУ ЦИКЛАМИ
        cycle_delay_frame = tk.Frame(cycle_frame, bg='#2d2d2d')
        cycle_delay_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Label(cycle_delay_frame, text="Задержка между циклами (сек):", bg='#2d2d2d', fg='white').pack(side=tk.LEFT)
        self.cycle_delay_var = tk.DoubleVar(value=0.0)
        cycle_delay_spinbox = tk.Spinbox(cycle_delay_frame, from_=0, to=3600, increment=0.1, 
                                         textvariable=self.cycle_delay_var, width=10)
        cycle_delay_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Управление точками
        points_frame = tk.LabelFrame(root, text="📍 Точки клика", 
                                     font=("Arial", 12, "bold"), bg='#2d2d2d', fg='white')
        points_frame.pack(pady=10, padx=10, fill='x')
        
        # Список точек
        self.points_listbox = tk.Listbox(points_frame, height=6, bg='#1e1e1e', fg='#00ff00',
                                         font=("Courier", 10), selectbackground='#4a9eff')
        self.points_listbox.pack(pady=5, padx=10, fill='x')
        
        # Кнопки управления точками
        points_btn_frame = tk.Frame(points_frame, bg='#2d2d2d')
        points_btn_frame.pack(pady=5, padx=10, fill='x')
        
        tk.Button(points_btn_frame, text="➕ Добавить (A)", 
                 command=self.add_point, bg='#28a745', fg='white').pack(side=tk.LEFT, padx=5)
        tk.Button(points_btn_frame, text="🗑️ Очистить (C)", 
                 command=self.clear_points, bg='#dc3545', fg='white').pack(side=tk.LEFT, padx=5)
        
        # Статистика
        stats_frame = tk.LabelFrame(root, text="📊 Статистика", 
                                    font=("Arial", 12, "bold"), bg='#2d2d2d', fg='white')
        stats_frame.pack(pady=10, padx=10, fill='x')
        
        self.clicks_label = tk.Label(stats_frame, text="Кликов: 0", 
                                    bg='#2d2d2d', fg='#00ff00', font=("Arial", 12))
        self.clicks_label.pack(pady=3)
        
        self.cycle_label = tk.Label(stats_frame, text="Цикл: 0 / 1", 
                                   bg='#2d2d2d', fg='yellow', font=("Arial", 12))
        self.cycle_label.pack(pady=3)
        
        self.points_label = tk.Label(stats_frame, text="Точек: 0", 
                                    bg='#2d2d2d', fg='#4a9eff', font=("Arial", 12))
        self.points_label.pack(pady=3)
        
        # Кнопки управления
        control_frame = tk.Frame(root, bg='#1e1e1e')
        control_frame.pack(pady=15)
        
        self.start_btn = tk.Button(control_frame, text="▶️ СТАРТ (V)", 
                                   command=self.start_clicking, 
                                   bg='#28a745', fg='white', font=("Arial", 12, "bold"),
                                   width=15, height=2)
        self.start_btn.pack(side=tk.LEFT, padx=10)
        
        self.stop_btn = tk.Button(control_frame, text="⏹️ СТОП (V)", 
                                  command=self.stop_clicking, 
                                  bg='#dc3545', fg='white', font=("Arial", 12, "bold"),
                                  width=15, height=2)
        self.stop_btn.pack(side=tk.LEFT, padx=10)
        
        # Инструкция
        info = tk.Label(root, 
                       text="Горячие клавиши:\nV - Старт/Стоп | A - Добавить точку | C - Очистить | B - Выход",
                       font=("Arial", 9), bg='#1e1e1e', fg='gray')
        info.pack(pady=10)
        
        # Статус
        self.status_var = tk.StringVar(value="⏸️ Остановлен")
        self.status_label = tk.Label(root, textvariable=self.status_var, 
                                    font=("Arial", 12, "bold"), bg='#1e1e1e', fg='red')
        self.status_label.pack(pady=5)
        
        # Запуск обновления статистики
        self.update_stats()
        
    def add_point(self):
        x, y = self.autoclicker.add_point()
        self.points_listbox.insert(tk.END, f"Точка {len(self.autoclicker.click_points)}: ({x}, {y})")
        self.update_points_label()
        
    def clear_points(self):
        self.autoclicker.clear_points()
        self.points_listbox.delete(0, tk.END)
        self.update_points_label()
        
    def update_points_label(self):
        count = len(self.autoclicker.click_points)
        self.points_label.config(text=f"Точек: {count}")
        
    def start_clicking(self):
        self.autoclicker.delay = self.delay_var.get()
        self.autoclicker.delay_variation = self.var_var.get()
        self.autoclicker.cycles = self.cycles_var.get()
        self.autoclicker.cycle_delay = self.cycle_delay_var.get()  # 🆕 Применяем задержку
        
        if self.autoclicker.start():
            self.status_var.set("✅ РАБОТАЕТ...")
            self.status_label.config(fg='#00ff00')
            self.cycle_label.config(text=f"Цикл: 1 / {self.cycles_var.get()}")
    
    def stop_clicking(self):
        if self.autoclicker.stop():
            self.status_var.set("️ Остановлен")
            self.status_label.config(fg='red')
    
    def update_stats(self):
        clicks = self.autoclicker.click_count
        cycles = self.autoclicker.current_cycle
        total_cycles = self.autoclicker.cycles
        
        self.clicks_label.config(text=f"Кликов: {clicks}")
        self.cycle_label.config(text=f"Цикл: {cycles + 1} / {total_cycles}")
        
        self.root.after(100, self.update_stats)

if __name__ == "__main__":
    print("🎮 Advanced AutoClicker запущен!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V - Старт/Стоп")
    print("A - Добавить точку")
    print("C - Очистить точки")
    print("B - Выход")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    root = tk.Tk()
    app = AdvancedClickerGUI(root)
    root.mainloop()
