import time
import threading
import random
from pynput.mouse import Button, Controller
from pynput.keyboard import Listener, KeyCode
import tkinter as tk
from tkinter import ttk

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
                self.mouse.click(Button.left)
                self.click_count += 1
                self.total_clicks += 1
                time.sleep(self.get_random_delay())
            else:
                x, y = self.click_points[self.current_point_index]
                self.mouse.position = (x, y)
                time.sleep(0.05)
                self.mouse.click(Button.left)
                
                self.click_count += 1
                self.total_clicks += 1
                
                self.current_point_index += 1
                
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
        self.root.geometry("700x800")
        self.root.resizable(False, False)
        
        # Цветовая схема
        self.colors = {
            'bg_primary': '#0f0f23',
            'bg_secondary': '#1a1a2e',
            'bg_card': '#16213e',
            'accent_primary': '#e94560',
            'accent_secondary': '#0f3460',
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
        
        # Настройка стилей
        style.configure('TFrame', background=self.colors['bg_secondary'])
        style.configure('TLabel', background=self.colors['bg_secondary'], 
                       foreground=self.colors['text_primary'], font=('Segoe UI', 10))
        style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'), 
                       foreground=self.colors['accent_primary'])
        style.configure('Card.TFrame', background=self.colors['bg_card'])
        
        style.configure('Primary.TButton', font=('Segoe UI', 11, 'bold'),
                       background=self.colors['accent_primary'], foreground='white')
        style.map('Primary.TButton',
                 background=[('active', '#ff6b6b'), ('pressed', '#c92a3d')])
        
        style.configure('Success.TButton', font=('Segoe UI', 11, 'bold'),
                       background=self.colors['success'], foreground='white')
        style.map('Success.TButton',
                 background=[('active', '#00f5b8'), ('pressed', '#00b886')])
        
        style.configure('Danger.TButton', font=('Segoe UI', 11, 'bold'),
                       background=self.colors['danger'], foreground='white')
        style.map('Danger.TButton',
                 background=[('active', '#ff6b7a'), ('pressed', '#e0384a')])
        
    def create_widgets(self):
        # Главный контейнер
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Заголовок
        self.create_header(main_container)
        
        # Карточка режима захвата
        self.create_capture_card(main_container)
        
        # Карточка настроек
        self.create_settings_card(main_container)
        
        # Карточка точек
        self.create_points_card(main_container)
        
        # Карточка статистики
        self.create_stats_card(main_container)
        
        # Кнопки управления
        self.create_control_buttons(main_container)
        
        # Футер
        self.create_footer(main_container)
        
    def create_header(self, parent):
        header_frame = tk.Frame(parent, bg=self.colors['bg_secondary'], height=80)
        header_frame.pack(fill='x', pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title = tk.Label(header_frame, text="🎮 AutoClicker PRO", 
                        font=('Segoe UI', 24, 'bold'),
                        bg=self.colors['bg_secondary'],
                        fg=self.colors['accent_primary'])
        title.pack(pady=20)
        
        subtitle = tk.Label(header_frame, text="Advanced Automation Tool",
                           font=('Segoe UI', 9),
                           bg=self.colors['bg_secondary'],
                           fg=self.colors['text_secondary'])
        subtitle.pack()
        
    def create_capture_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='raised', borderwidth=0)
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        self.capture_btn = tk.Button(inner, text="🎯 РЕЖИМ ЗАХВАТА",
                                    command=self.toggle_capture_mode,
                                    bg=self.colors['warning'],
                                    fg='white',
                                    font=('Segoe UI', 12, 'bold'),
                                    relief='flat',
                                    padx=20,
                                    pady=10,
                                    cursor='hand2')
        self.capture_btn.pack(fill='x')
        
        self.capture_status = tk.Label(inner, text="❌ Выключен",
                                      bg=self.colors['bg_card'],
                                      fg=self.colors['text_secondary'],
                                      font=('Segoe UI', 9))
        self.capture_status.pack(pady=(5, 0))
        
    def create_settings_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='raised', borderwidth=0)
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        # Заголовок
        title = tk.Label(inner, text="⚙️ Настройки",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_card'],
                        fg=self.colors['text_primary'])
        title.pack(anchor='w', pady=(0, 15))
        
        # Задержка
        self.create_setting_row(inner, "Задержка (сек):", self.delay_var if hasattr(self, 'delay_var') else None, 0.1, 0.001, 10, 0.01)
        
        if not hasattr(self, 'delay_var'):
            self.delay_var = tk.DoubleVar(value=0.1)
        
        # Вариация
        self.create_setting_row(inner, "Вариация (сек):", self.var_var if hasattr(self, 'var_var') else None, 0.02, 0, 1, 0.01)
        
        if not hasattr(self, 'var_var'):
            self.var_var = tk.DoubleVar(value=0.02)
        
        # Циклы
        self.create_setting_row(inner, "Количество циклов:", self.cycles_var if hasattr(self, 'cycles_var') else None, 1, 1, 9999, 1, is_int=True)
        
        if not hasattr(self, 'cycles_var'):
            self.cycles_var = tk.IntVar(value=1)
        
        # Задержка между циклами
        self.create_setting_row(inner, "Задержка между циклами:", self.cycle_delay_var if hasattr(self, 'cycle_delay_var') else None, 0.0, 0, 3600, 0.1)
        
        if not hasattr(self, 'cycle_delay_var'):
            self.cycle_delay_var = tk.DoubleVar(value=0.0)
        
    def create_setting_row(self, parent, label_text, variable, value, from_, to, increment, is_int=False):
        frame = tk.Frame(parent, bg=self.colors['bg_card'])
        frame.pack(fill='x', pady=5)
        
        label = tk.Label(frame, text=label_text,
                        bg=self.colors['bg_card'],
                        fg=self.colors['text_secondary'],
                        font=('Segoe UI', 10))
        label.pack(side='left')
        
        if is_int:
            var = tk.IntVar(value=value) if variable is None else variable
            spinbox = tk.Spinbox(frame, from_=from_, to=to, increment=increment,
                                textvariable=var, width=12,
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'],
                                relief='flat',
                                font=('Segoe UI', 10))
        else:
            var = tk.DoubleVar(value=value) if variable is None else variable
            spinbox = tk.Spinbox(frame, from_=from_, to=to, increment=increment,
                                textvariable=var, width=12,
                                bg=self.colors['bg_secondary'],
                                fg=self.colors['text_primary'],
                                relief='flat',
                                font=('Segoe UI', 10))
        spinbox.pack(side='right')
        
        if variable is None:
            if 'delay_var' not in dir(self) and 'Задержка (сек)' in label_text:
                self.delay_var = var
            elif 'var_var' not in dir(self) and 'Вариация' in label_text:
                self.var_var = var
            elif 'cycles_var' not in dir(self) and 'Количество циклов' in label_text:
                self.cycles_var = var
            elif 'cycle_delay_var' not in dir(self) and 'Задержка между циклами' in label_text:
                self.cycle_delay_var = var
        
    def create_points_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='raised', borderwidth=0)
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='both', expand=True, padx=20, pady=15)
        
        # Заголовок
        title = tk.Label(inner, text="📍 Точки клика",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_card'],
                        fg=self.colors['text_primary'])
        title.pack(anchor='w', pady=(0, 10))
        
        # Список точек
        list_frame = tk.Frame(inner, bg=self.colors['bg_secondary'])
        list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        self.points_listbox = tk.Listbox(list_frame, height=8,
                                        bg=self.colors['bg_secondary'],
                                        fg=self.colors['success'],
                                        font=('Consolas', 10),
                                        selectbackground=self.colors['info'],
                                        selectforeground='white',
                                        relief='flat',
                                        highlightthickness=0)
        self.points_listbox.pack(side='left', fill='both', expand=True, padx=10, pady=10)
        
        scrollbar = ttk.Scrollbar(self.points_listbox)
        scrollbar.pack(side='right', fill='y')
        self.points_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.points_listbox.yview)
        
        # Кнопки
        btn_frame = tk.Frame(inner, bg=self.colors['bg_card'])
        btn_frame.pack(fill='x')
        
        tk.Button(btn_frame, text="➕ Добавить (A)",
                 command=self.add_point_manual,
                 bg=self.colors['success'],
                 fg='white',
                 font=('Segoe UI', 10, 'bold'),
                 relief='flat',
                 padx=15,
                 pady=8,
                 cursor='hand2').pack(side='left', padx=(0, 10))
        
        tk.Button(btn_frame, text="🗑️ Очистить (C)",
                 command=self.clear_points,
                 bg=self.colors['danger'],
                 fg='white',
                 font=('Segoe UI', 10, 'bold'),
                 relief='flat',
                 padx=15,
                 pady=8,
                 cursor='hand2').pack(side='left')
        
        self.points_count_label = tk.Label(inner, text="Точек: 0",
                                          bg=self.colors['bg_card'],
                                          fg=self.colors['info'],
                                          font=('Segoe UI', 10, 'bold'))
        self.points_count_label.pack(pady=(10, 0))
        
    def create_stats_card(self, parent):
        card = tk.Frame(parent, bg=self.colors['bg_card'], relief='raised', borderwidth=0)
        card.pack(fill='x', pady=(0, 15))
        
        inner = tk.Frame(card, bg=self.colors['bg_card'])
        inner.pack(fill='x', padx=20, pady=15)
        
        # Заголовок
        title = tk.Label(inner, text="📊 Статистика",
                        font=('Segoe UI', 14, 'bold'),
                        bg=self.colors['bg_card'],
                        fg=self.colors['text_primary'])
        title.pack(anchor='w', pady=(0, 15))
        
        # Статистика в 3 колонки
        stats_frame = tk.Frame(inner, bg=self.colors['bg_card'])
        stats_frame.pack(fill='x')
        
        self.clicks_stat = self.create_stat_box(stats_frame, "Кликов", "0", self.colors['success'])
        self.clicks_stat.pack(side='left', fill='both', expand=True, padx=5)
        
        self.cycle_stat = self.create_stat_box(stats_frame, "Цикл", "0 / 1", self.colors['warning'])
        self.cycle_stat.pack(side='left', fill='both', expand=True, padx=5)
        
        self.total_stat = self.create_stat_box(stats_frame, "Всего кликов", "0", self.colors['info'])
        self.total_stat.pack(side='left', fill='both', expand=True, padx=5)
        
    def create_stat_box(self, parent, label_text, value_text, color):
        frame = tk.Frame(parent, bg=self.colors['bg_secondary'], relief='raised', borderwidth=0)
        frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        label = tk.Label(frame, text=label_text,
                        bg=self.colors['bg_secondary'],
                        fg=self.colors['text_secondary'],
                        font=('Segoe UI', 9))
        label.pack(pady=(10, 5))
        
        value = tk.Label(frame, text=value_text,
                        bg=self.colors['bg_secondary'],
                        fg=color,
                        font=('Segoe UI', 16, 'bold'))
        value.pack(pady=(0, 10))
        
        return frame
        
    def create_control_buttons(self, parent):
        btn_frame = tk.Frame(parent, bg=self.colors['bg_primary'])
        btn_frame.pack(fill='x', pady=10)
        
        self.start_btn = tk.Button(btn_frame, text="▶️ ЗАПУСТИТЬ (V)",
                                  command=self.start_clicking,
                                  bg=self.colors['success'],
                                  fg='white',
                                  font=('Segoe UI', 14, 'bold'),
                                  relief='flat',
                                  padx=30,
                                  pady=15,
                                  cursor='hand2')
        self.start_btn.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.stop_btn = tk.Button(btn_frame, text="⏹️ ОСТАНОВИТЬ (V)",
                                 command=self.stop_clicking,
                                 bg=self.colors['danger'],
                                 fg='white',
                                 font=('Segoe UI', 14, 'bold'),
                                 relief='flat',
                                 padx=30,
                                 pady=15,
                                 cursor='hand2')
        self.stop_btn.pack(side='left', fill='both', expand=True, padx=(10, 0))
        
    def create_footer(self, parent):
        footer = tk.Frame(parent, bg=self.colors['bg_primary'])
        footer.pack(fill='x', pady=(15, 0))
        
        info = tk.Label(footer, 
                       text="V - Старт/Стоп | A - Добавить точку | X - Режим захвата | C - Очистить | B - Выход",
                       font=('Segoe UI', 8),
                       bg=self.colors['bg_primary'],
                       fg=self.colors['text_secondary'])
        info.pack(pady=5)
        
        self.status_label = tk.Label(footer, text="⏸️ Остановлен",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=self.colors['bg_primary'],
                                    fg=self.colors['text_secondary'])
        self.status_label.pack(pady=5)
        
    def toggle_capture_mode(self):
        self.autoclicker.capture_mode = not self.autoclicker.capture_mode
        
        if self.autoclicker.capture_mode:
            self.capture_btn.config(bg=self.colors['accent_primary'], 
                                   text="🎯 КЛИКНИ В ЛЮБОЕ МЕСТО!")
            self.capture_status.config(text="✅ АКТИВЕН (кликни левой кнопкой)", 
                                      fg=self.colors['success'])
        else:
            self.capture_btn.config(bg=self.colors['warning'], 
                                   text="🎯 РЕЖИМ ЗАХВАТА")
            self.capture_status.config(text="❌ Выключен", 
                                      fg=self.colors['text_secondary'])
        
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
            
            for widget in self.clicks_stat.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('text') != "Кликов":
                    widget.config(text=str(clicks))
                    break
            
            for widget in self.cycle_stat.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('text') != "Цикл":
                    widget.config(text=f"{cycles + 1} / {total_cycles}")
                    break
            
            for widget in self.total_stat.winfo_children():
                if isinstance(widget, tk.Label) and widget.cget('text') != "Всего кликов":
                    widget.config(text=str(total))
                    break
        
        self.root.after(100, self.update_stats)

if __name__ == "__main__":
    print("🎮 AutoClicker PRO запущен!")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("V - Старт/Стоп")
    print("A - Добавить точку")
    print("X - Режим захвата")
    print("C - Очистить точки")
    print("B - Выход")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    
    root = tk.Tk()
    app = ModernClickerGUI(root)
    root.mainloop()
