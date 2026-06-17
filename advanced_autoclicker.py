import tkinter as tk
from tkinter import filedialog, messagebox
import threading
import time
import random
import json

from pynput.mouse import Controller as MouseController, Button
from pynput.keyboard import Listener, KeyCode


class AutoClicker:

    def __init__(self):
        self.mouse = MouseController()

        self.click_points = []

        self.delay = 0.5
        self.delay_variation = 0.2
        self.cycle_delay = 1.0
        self.cycles = 0

        self.clicking = False
        self.running = True

    def add_point(self):
        pos = self.mouse.position
        self.click_points.append(pos)
        return pos

    def clear_points(self):
        self.click_points.clear()

    def start(self):
        if self.clicking:
            return

        if not self.click_points:
            return

        self.clicking = True

        threading.Thread(
            target=self.click_loop,
            daemon=True
        ).start()

    def stop(self):
        self.clicking = False

    def click_loop(self):
        cycle = 0

        while self.clicking:

            if self.cycles > 0 and cycle >= self.cycles:
                break

            for point in self.click_points:

                if not self.clicking:
                    break

                self.mouse.position = point

                self.mouse.click(Button.left)

                delay = random.uniform(
                    max(0.01, self.delay - self.delay_variation),
                    self.delay + self.delay_variation
                )

                time.sleep(delay)

            cycle += 1

            if self.cycle_delay > 0:
                time.sleep(self.cycle_delay)

        self.clicking = False

    def save_profile(self, filename):

        data = {
            "click_points": self.click_points,
            "delay": self.delay,
            "delay_variation": self.delay_variation,
            "cycle_delay": self.cycle_delay,
            "cycles": self.cycles
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_profile(self, filename):

        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.click_points = [
            tuple(p) for p in data.get("click_points", [])
        ]

        self.delay = data.get("delay", 0.5)
        self.delay_variation = data.get("delay_variation", 0.2)
        self.cycle_delay = data.get("cycle_delay", 1.0)
        self.cycles = data.get("cycles", 0)


class AutoClickerGUI:

    def __init__(self, root):

        self.root = root
        self.root.title("Advanced AutoClicker")
        self.root.geometry("500x500")

        self.clicker = AutoClicker()

        self.create_widgets()

        self.listener = Listener(on_press=self.on_key)
        self.listener.start()

    def create_widgets(self):

        tk.Label(
            self.root,
            text="Точки клика"
        ).pack()

        self.listbox = tk.Listbox(
            self.root,
            height=10
        )
        self.listbox.pack(fill="x", padx=10)

        tk.Label(self.root, text="Задержка").pack()
        self.delay_entry = tk.Entry(self.root)
        self.delay_entry.insert(0, "0.5")
        self.delay_entry.pack()

        tk.Label(self.root, text="Разброс").pack()
        self.variation_entry = tk.Entry(self.root)
        self.variation_entry.insert(0, "0.2")
        self.variation_entry.pack()

        tk.Label(self.root, text="Пауза между циклами").pack()
        self.cycle_entry = tk.Entry(self.root)
        self.cycle_entry.insert(0, "1.0")
        self.cycle_entry.pack()

        tk.Label(self.root, text="Количество циклов (0=бесконечно)").pack()
        self.cycles_entry = tk.Entry(self.root)
        self.cycles_entry.insert(0, "0")
        self.cycles_entry.pack()

        tk.Button(
            self.root,
            text="Добавить точку",
            command=self.add_point
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(
            self.root,
            text="Очистить точки",
            command=self.clear_points
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(
            self.root,
            text="Старт",
            command=self.start
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(
            self.root,
            text="Стоп",
            command=self.stop
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(
            self.root,
            text="Сохранить профиль",
            command=self.save_profile
        ).pack(fill="x", padx=10, pady=2)

        tk.Button(
            self.root,
            text="Загрузить профиль",
            command=self.load_profile
        ).pack(fill="x", padx=10, pady=2)

        self.status = tk.Label(
            self.root,
            text="F6 Старт | F7 Стоп | F8 Добавить точку"
        )

        self.status.pack(pady=10)

    def refresh_points(self):

        self.listbox.delete(0, tk.END)

        for i, point in enumerate(self.clicker.click_points):
            self.listbox.insert(
                tk.END,
                f"{i + 1}. {point[0]}, {point[1]}"
            )

    def add_point(self):

        point = self.clicker.add_point()

        self.listbox.insert(
            tk.END,
            f"{len(self.clicker.click_points)}. {point[0]}, {point[1]}"
        )

    def clear_points(self):

        self.clicker.clear_points()
        self.refresh_points()

    def update_settings(self):

        self.clicker.delay = float(self.delay_entry.get())
        self.clicker.delay_variation = float(
            self.variation_entry.get()
        )
        self.clicker.cycle_delay = float(
            self.cycle_entry.get()
        )
        self.clicker.cycles = int(
            self.cycles_entry.get()
        )

    def start(self):

        try:
            self.update_settings()
            self.clicker.start()

        except Exception as e:
            messagebox.showerror(
                "Ошибка",
                str(e)
            )

    def stop(self):
        self.clicker.stop()

    def save_profile(self):

        filename = filedialog.asksaveasfilename(
            defaultextension=".json"
        )

        if not filename:
            return

        self.update_settings()

        self.clicker.save_profile(filename)

    def load_profile(self):

        filename = filedialog.askopenfilename(
            filetypes=[("JSON", "*.json")]
        )

        if not filename:
            return

        self.clicker.load_profile(filename)

        self.delay_entry.delete(0, tk.END)
        self.delay_entry.insert(0, str(self.clicker.delay))

        self.variation_entry.delete(0, tk.END)
        self.variation_entry.insert(
            0,
            str(self.clicker.delay_variation)
        )

        self.cycle_entry.delete(0, tk.END)
        self.cycle_entry.insert(
            0,
            str(self.clicker.cycle_delay)
        )

        self.cycles_entry.delete(0, tk.END)
        self.cycles_entry.insert(
            0,
            str(self.clicker.cycles)
        )

        self.refresh_points()

    def on_key(self, key):

        try:

            if key == KeyCode.from_char(""):
                pass

            if key == KeyCode(vk=117):
                self.start()

            elif key == KeyCode(vk=118):
                self.stop()

            elif key == KeyCode(vk=119):
                self.add_point()

        except Exception:
            pass


def main():

    root = tk.Tk()

    AutoClickerGUI(root)

    root.mainloop()


if __name__ == "__main__":
    main()
