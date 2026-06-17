import time
import threading
import random
from pynput.mouse import Button, Controller, Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, KeyCode, Key
import tkinter as tk
from tkinter import ttk
import json
from tkinter import filedialog, messagebox
class ModernAutoClicker:
    def __init__(self):
        self.mouse = Controller()
        self.clicking = False
        self.running = True
        self.capture_mode = False
        
        self.click_points = []
        self.current_point_index = 0
        self.delay = 0.1
        self.delay_variation = 0.02
        self.cycle_delay = 0.0
        self.cycles = 1
        self.current_cycle = 0
        self.click_count = 0
        self.total_clicks = 0
        
        self.toggle_key = KeyCode(char='v')
        self.exit_key = KeyCode(char='b')
        self.add_point_key = KeyCode(char='a')
        self.clear_points_key = KeyCode(char='c')
        self.capture_key = KeyCode(char='x')
        
    def get_random_delay(self):
        return max(0.001, self.delay + random.uniform(-self.delay_variation, self.delay_variation))
    
    def click_loop(self):
        while self.clicking and self.running:
            if not self.click_points:
                # Если нет точек, кликаем где стоит курсор
                self.mouse.click(Button.left)
                self.click_count += 1
                self.total_clicks += 1
                time.sleep(self.get_random_delay())
            else:
                # Логика работы с точками
                x, y = self.click_points[self.current_point_index]
                
                # 1. Перемещаем мышь
                self.mouse.position = (x, y)
                # 2. Ждем, чтобы ты увидел движение
                time.sleep(0.15) 
                
                # 3. Кликаем
                self.mouse.click(Button.left)
                
                self.click_count += 1
                self.total_clicks += 1
                
                self.current_point_index += 1
                
                # Проверка конца списка точек
                if self.current_point_index >= len(self.click_points):
                    self.current_point_index = 0
                    self.current_cycle += 1
                    
                    if self.current_cycle >= self.cycles:
                        self.clicking = False
                        break
                    else:
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
    
    def add_point(self, x=None, y=None):
        if x is None or y is None:
            x, y = self.mouse.position
        self.click_points.append((x, y))
        return x, y
    
    def clear_points(self):
        self.click_points.clear()
        self.current_point_index = 0
    def save_profile(self, filename="profile.json"):
    data = {
        "click_points": self.click_points,
        "delay": self.delay,
        "delay_variation": self.delay_variation,
        "cycle_delay": self.cycle_delay,
        "cycles": self.cycles
    }

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def load_profile(self, filename="profile.json"):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.click_points = data.get("click_points", [])
        self.delay = data.get("delay", 0.1)
        self.delay_variation = data.get("delay_variation", 0.02)
        self.cycle_delay = data.get("cycle_delay", 0.0)
        self.cycles = data.get("cycles", 1)

        return True

    except Exception as e:
        print(f"Ошибка загрузки профиля: {e}")
        return False
    def on_press(self, key):
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
            x, y = self.add_point()
            if hasattr(self, 'gui') and self.gui:
                self.gui.add_point_to_list(x, y)
        elif key == self.clear_points_key:
            self.clear_points()
            if hasattr(self, 'gui') and self.gui:
                self.gui.clear_points_list()
        elif key == self.capture_key:
            self.capture_mode = not self.capture_mode
            if hasattr(self, 'gui') and self.gui:
                self.gui.toggle_capture_mode()

class ModernClickerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎮 AutoClicker PRO")
        self.root.geometry("700x1100")  # УВЕЛИЧЕННАЯ ВЫСОТА
        self.root.resizable(False, False)
        
        self.colors = {
            'bg_primary': '#0f0f23',
            'bg_secondary': '#1a1a2e',
            'bg_card': '#16213e',
            'accent_primary': '#e94560',
            'text_primary': '#ffffff',
            'text_secondary': '#a0a0a0',
            'success': '#00d9a3',
            'warning': '#ffc107',
            'danger': '#ff4757',
            'info': '#4a9eff'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        self.autoclicker = ModernAutoClicker()
        self.autoclicker.gui = self
        
        self.setup_styles()
        self.create_widgets()
        self.update_stats()
        
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors['bg_secondary'])
        style.configure('TLabel', background=self.colors['bg_secondary'], 
                       foreground=self.colors['text_primary'], font=('Segoe UI', 10))
        
    def create_widgets(self):
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        self.create_header(main_container)
        self.create_capture_card(main_container)
        self.create_settings_card(main_container)
        self.create_points_card(main_container)
        self.create_stats_card(main_container)
        self.create_control_buttons(main_container)
        self.create_footer(main_container)
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=80)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        tk.Label(header_frame, text="🎮 AutoClicker PRO", 
                font=('Segoe UI', 24, 'bold'),
                bg=self.colors['bg_secondary'],
                fg=self.colors['accent_primary']).pack(pady=20)
        
    def create_capture_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        self.capture_btn = tk.Button(inner, text="🎯 РЕЖИМ ЗАХВАТА",
                                    command=self.toggle_capture_mode,
                                    bg=self.colors['warning'], fg='white',
                                    font=('Segoe UI', 12, 'bold'), relief='flat',
                                    padx=20, pady=10, cursor='hand2')
        self.capture_btn.pack(fill='x')
        
        self.capture_status = tk.Label(inner, text="❌ Выключен",
                                      bg=self.colors['bg_card'],
                                      fg=self.colors['text_secondary'],
                                      font=('Segoe UI', 9))
        self.capture_status.pack(pady=(5, 0))
        
    def create_settings_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        tk.Label(inner, text="⚙️ Настройки", font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        self.delay_var = tk.DoubleVar(value=0.1)
        self.var_var = tk.DoubleVar(value=0.02)
        self.cycles_var = tk.IntVar(value=1)
        self.cycle_delay_var = tk.DoubleVar(value=0.0)
        
        self.create_setting_row(inner, "Задержка (сек):", self.delay_var, 0.001, 10, 0.01)
        self.create_setting_row(inner, "Вариация (сек):", self.var_var, 0, 1, 0.01)
        self.create_setting_row(inner, "Количество циклов:", self.cycles_var, 1, 9999, 1, True)
        self.create_setting_row(inner, "Задержка между циклами:", self.cycle_delay_var, 0, 3600, 0.1)
        
    def create_setting_row(self, parent, label_text, variable, from_, to, increment, is_int=False):
        frame = tk.Frame(parent, bg=self.colors['bg_card'])
        frame.pack(fill='x', pady=5)
        
        tk.Label(frame, text=label_text, bg=self.colors['bg_card'],
                fg=self.colors['text_secondary'], font=('Segoe UI', 10)).pack(side='left')
        
        spinbox = tk.Spinbox(frame, from_=from_, to=to, increment=increment,
                            textvariable=variable, width=12,
                            bg=self.colors['bg_secondary'], fg=self.colors['text_primary'],
                            relief='flat', font=('Segoe UI', 10))
        spinbox.pack(side='right')
        
    def create_points_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='both', expand=True, padx=20, pady=15)
        
        tk.Label(inner, text=" Точки клика", font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 10))
        
        list_frame = tk.Frame(inner, bg=self.colors['bg_secondary'])
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.points_listbox = tk.Listbox(list_frame, height=6,
                                        bg=self.colors['bg_secondary'], fg=self.colors['success'],
                                        font=('Consolas', 10), selectbackground=self.colors['info'],
                                        selectforeground='white', relief='flat', highlightthickness=0)
        self.points_listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.points_listbox)
        scrollbar.pack(side='right', fill='y')
        self.points_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.points_listbox.yview)
        
        btn_frame = tk.Frame(inner, bg=self.colors['bg_card'])
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="➕ Добавить (A)", command=self.add_point_manual,
                 bg=self.colors['success'], fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left', padx=(0, 10))
        
        tk.Button(btn_frame, text="🗑️ Очистить (C)", command=self.clear_points,
                 bg=self.colors['danger'], fg='white', font=('Segoe UI', 10, 'bold'),
                 relief='flat', padx=15, pady=8, cursor='hand2').pack(side='left')
        
        self.points_count_label = tk.Label(inner, text="Точек: 0",
                                          bg=self.colors['bg_card'], fg=self.colors['info'],
                                          font=('Segoe UI', 10, 'bold'))
        self.points_count_label.pack(pady=(10, 0))
        
    def create_stats_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        tk.Label(inner, text="📊 Статистика", font=('Segoe UI', 14, 'bold'),
                bg=self.colors['bg_card'], fg=self.colors['text_primary']).pack(anchor='w', pady=(0, 15))
        
        stats_frame = tk.Frame(inner, bg=self.colors['bg_card'])
        stats_frame.pack(fill='x')
        
        self.clicks_stat = self.create_stat_box(stats_frame, "Кликов", "0", self.colors['success'])
        self.clicks_stat.pack(side='left', fill='both', expand=True, padx=5)
        
        self.cycle_stat = self.create_stat_box(stats_frame, "Цикл", "0 / 1", self.colors['warning'])
        self.cycle_stat.pack(side='left', fill='both', expand=True, padx=5)
        
        self.total_stat = self.create_stat_box(stats_frame, "Всего кликов", "0", self.colors['info'])
        self.total_stat.pack(side='left', fill='both', expand=True, padx=5)
        
    def create_stat_box(self, parent, label_text, value_text, color):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'])
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        tk.Label(frame, text=label_text, bg=self.colors['bg_secondary'],
                fg=self.colors['text_secondary'], font=('Segoe UI', 9)).pack(pady=(10, 5))
        
        tk.Label(frame, text=value_text, bg=self.colors['bg_secondary'],
                fg=color, font=('Segoe UI', 16, 'bold')).pack(pady=(0, 10))
        
        return frame
        
    def create_control_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        btn_frame.pack(fill='x', pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="▶️ ЗАПУСТИТЬ (V)",
                                  command=self.start_clicking, bg=self.colors['success'], fg='white',
                                  font=('Segoe UI', 14, 'bold'), relief='flat', padx=30, pady=15, cursor='hand2')
        self.start_btn.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="️ ОСТАНОВИТЬ (V)",
                                 command=self.stop_clicking, bg=self.colors['danger'], fg='white',
                                 font=('Segoe UI', 14, 'bold'), relief='flat', padx=30, pady=15, cursor='hand2')
        self.stop_btn.pack(side='left', fill='both', expand=True, padx=(10, 0))
        # Кнопки профилей
profile_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
profile_frame.pack(fill='x', pady=(10, 0))

tk.Button(
    profile_frame,
    text="💾 Сохранить профиль",
    command=lambda: self.autoclicker.save_profile(),
    bg=self.colors['accent_primary'],
    fg='white',
    font=('Segoe UI', 10, 'bold'),
    relief='flat',
    cursor='hand2'
).pack(side='left', fill='x', expand=True, padx=(0, 5))

tk.Button(
    profile_frame,
    text="📂 Загрузить профиль",
    command=self.load_profile_gui,
    bg=self.colors['accent_secondary'],
    fg='white',
    font=('Segoe UI', 10, 'bold'),
    relief='flat',
    cursor='hand2'
).pack(side='left', fill='x', expand=True, padx=(5, 0))
    def create_footer(self, parent):
        footer = tk.Frame(parent, bg=self.colors['bg_primary'])
        footer.pack(fill='x', pady=(15, 0))
        
        tk.Label(footer, text="V - Старт/Стоп | A - Добавить точку | X - Режим захвата | C - Очистить | B - Выход",
                font=('Segoe UI', 8), bg=self.colors['bg_primary'], fg=self.colors['text_secondary']).pack(pady=5)
        
        self.status_label = tk.Label(footer, text="⏸️ Остановлен", font=('Segoe UI', 11, 'bold'),
                                    bg=self.colors['bg_primary'], fg=self.colors['text_secondary'])
        self.status_label.pack(pady=5)
        
    def toggle_capture_mode(self):
        self.autoclicker.capture_mode = not self.autoclicker.capture_mode
        
        if self.autoclicker.capture_mode:
            self.capture_btn.config(bg=self.colors['accent_primary'], text=" КЛИКНИ В ЛЮБОЕ МЕСТО!")
            self.capture_status.config(text="✅ АКТИВЕН (кликни левой кнопкой)", fg=self.colors['success'])
        else:
            self.capture_btn.config(bg=self.colors['warning'], text=" РЕЖИМ ЗАХВАТА")
            self.capture_status.config(text="❌ Выключен", fg=self.colors['text_secondary'])
        
    def add_point_manual(self):
        x, y = self.autoclicker.add_point()
        self.add_point_to_list(x, y)
        
    def add_point_to_list(self, x, y):
        point_num = len(self.autoclicker.click_points)
        self.points_listbox.insert(tk.END, f"#{point_num} → X: {x:4d} | Y: {y:4d}")
        self.points_listbox.see(tk.END)
        self.points_count_label.config(text=f"Точек: {point_num}")
        
    def clear_points(self):
        self.autoclicker.clear_points()
        self.clear_points_list()
        
    def clear_points_list(self):
        self.points_listbox.delete(0, tk.END)
        self.points_count_label.config(text="Точек: 0")
        
    def start_clicking(self):
        self.autoclicker.delay = self.delay_var.get()
        self.autoclicker.delay_variation = self.var_var.get()
        self.autoclicker.cycles = self.cycles_var.get()
        self.autoclicker.cycle_delay = self.cycle_delay_var.get()
        
        if self.autoclicker.start():
            self.status_label.config(text="✅ РАБОТАЕТ", fg=self.colors['success'])
            self.start_btn.config(state='disabled', bg=self.colors['text_secondary'])
            self.stop_btn.config(state='normal')
        
    def stop_clicking(self):
        if self.autoclicker.stop():
            self.status_label.config(text="⏸️ Остановлен", fg=self.colors['text_secondary'])
            self.start_btn.config(state='normal', bg=self.colors['success'])
            self.stop_btn.config(state='disabled')
    
    def update_stats(self):
        if hasattr(self, 'clicks_stat'):
            clicks = self.autoclicker.click_count
            total = self.autoclicker.total_clicks
            cycles = self.autoclicker.current_cycle
            total_cycles = self.autoclicker.cycles
            
            # Обновляем тексты в карточках статистики
            # (Упрощенная логика для обновления лейблов внутри карточек)
            # В реальном проекте лучше использовать отдельные переменные для лейблов
            
        self.root.after(100, self.update_stats)
def load_profile_gui(self):
    if self.autoclicker.load_profile():

        self.points_listbox.delete(0, tk.END)

        for i, point in enumerate(self.autoclicker.click_points, start=1):
            self.points_listbox.insert(
                tk.END,
                f"{i}. X={point[0]} Y={point[1]}"
            )

        self.update_stats()
        self.status_label.config(text="Профиль загружен")
if __name__ == "__main__":
    root = tk.Tk()
    app = ModernClickerGUI(root)
    root.mainloop()
