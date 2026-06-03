import sys
import threading
import time
import winsound
import customtkinter as ctk
from pynput import mouse, keyboard

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class AutoclickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clicker")
        self.root.geometry("320x440")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(fg_color=("#F0F0F0", "#202020"))

        self.is_running = False
        self.mouse_button = "ЛКМ"
        self.interval = 1.0
        self.start_delay = 0
        self.current_hotkey = "F5"
        self.click_count = 0
        self.kb_listener = None
        self.is_dark_theme = True

        self.mouse_controller = mouse.Controller()
        self.setup_ui()
        self.start_background_threads()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self):
        header_frame = ctk.CTkFrame(self.root, fg_color="transparent", height=40)
        header_frame.pack(fill="x", padx=20, pady=(15, 5))
        header_frame.pack_propagate(False)

        lbl_title = ctk.CTkLabel(header_frame, text="CLICKER", font=("Code Pro Regular", 14, "bold"), text_color=("#333333", "#FFFFFF"))
        lbl_title.pack(side="left")

        self.theme_btn = ctk.CTkButton(
            header_frame, 
            text="Т", 
            font=("Code Pro Regular", 11, "bold"),
            width=32, 
            height=32, 
            corner_radius=16,
            fg_color=("#E0E0E0", "#2C2C2C"),
            text_color=("#333333", "#FFFFFF"),
            hover_color=("#D0D0D0", "#404040"),
            command=self.toggle_theme
        )
        self.theme_btn.pack(side="right")
        self.theme_btn.pack_propagate(False)

        self.config_frame = ctk.CTkFrame(self.root, fg_color=("#FFFFFF", "#2C2C2C"), corner_radius=12, border_width=1, border_color=("#E0E0E0", "#444444"))
        self.config_frame.pack(fill="x", padx=20, pady=5)

        lbl_btn = ctk.CTkLabel(self.config_frame, text="Кнопка:", font=("Code Pro Regular", 13), text_color=("#333333", "#FFFFFF"))
        lbl_btn.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        
        self.btn_var = ctk.StringVar(value="ЛКМ")
        self.btn_menu = ctk.CTkComboBox(self.config_frame, variable=self.btn_var, values=["ЛКМ", "ПКМ"], state="readonly", width=90, height=32, corner_radius=6, fg_color=("#F5F5F5", "#1A1A1A"), border_color=("#E0E0E0", "#444444"), button_color=("#E0E0E0", "#444444"), text_color=("#333333", "#FFFFFF"), font=("Code Pro Regular", 12), dropdown_font=("Code Pro Regular", 12))
        self.btn_menu.grid(row=0, column=1, padx=20, pady=10, sticky="e")

        lbl_int = ctk.CTkLabel(self.config_frame, text="Интервал (сек):", font=("Code Pro Regular", 13), text_color=("#333333", "#FFFFFF"))
        lbl_int.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.int_entry = ctk.CTkEntry(self.config_frame, width=90, height=32, justify="center", corner_radius=6, fg_color=("#F5F5F5", "#1A1A1A"), border_color=("#E0E0E0", "#444444"), text_color=("#333333", "#FFFFFF"), font=("Code Pro Regular", 13))
        self.int_entry.insert(0, "1.0")
        self.int_entry.grid(row=1, column=1, padx=20, pady=10, sticky="e")

        lbl_delay = ctk.CTkLabel(self.config_frame, text="Задержка (сек):", font=("Code Pro Regular", 13), text_color=("#333333", "#FFFFFF"))
        lbl_delay.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.delay_entry = ctk.CTkEntry(self.config_frame, width=90, height=32, justify="center", corner_radius=6, fg_color=("#F5F5F5", "#1A1A1A"), border_color=("#E0E0E0", "#444444"), text_color=("#333333", "#FFFFFF"), font=("Code Pro Regular", 13))
        self.delay_entry.insert(0, "0")
        self.delay_entry.grid(row=2, column=1, padx=20, pady=10, sticky="e")

        lbl_hk = ctk.CTkLabel(self.config_frame, text="Горячая клавиша:", font=("Code Pro Regular", 13), text_color=("#333333", "#FFFFFF"))
        lbl_hk.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.hk_var = ctk.StringVar(value="F5")
        f_keys = [f"F{i}" for i in range(1, 13)]
        self.hk_menu = ctk.CTkComboBox(self.config_frame, variable=self.hk_var, values=f_keys, state="readonly", width=90, height=32, corner_radius=6, fg_color=("#F5F5F5", "#1A1A1A"), border_color=("#E0E0E0", "#444444"), button_color=("#E0E0E0", "#444444"), text_color=("#333333", "#FFFFFF"), font=("Code Pro Regular", 12), dropdown_font=("Code Pro Regular", 12), command=self.on_hotkey_change)
        self.hk_menu.grid(row=3, column=1, padx=20, pady=10, sticky="e")

        self.lbl_counter = ctk.CTkLabel(self.config_frame, text="Кликов сделано: 0", font=("Code Pro Regular", 12), text_color=("#666666", "#AAAAAA"))
        self.lbl_counter.grid(row=4, column=0, columnspan=2, padx=20, pady=(5, 12))

        self.toggle_btn = ctk.CTkButton(
            self.root, 
            text="СТАРТ (F5)", 
            font=("Code Pro Regular", 13, "bold"), 
            fg_color=("#E0E0E0", "#404040"), 
            text_color=("#333333", "#FFFFFF"),
            hover_color=("#D0D0D0", "#555555"),
            height=46,
            corner_radius=10,
            border_width=1,
            border_color=("#CCCCCC", "#555555"),
            command=self.toggle_clicking
        )
        self.toggle_btn.pack(fill="x", padx=20, pady=15)

    def toggle_theme(self):
        if self.is_dark_theme:
            ctk.set_appearance_mode("light")
            self.theme_btn.configure(text="С")
            self.is_dark_theme = False
        else:
            ctk.set_appearance_mode("dark")
            self.theme_btn.configure(text="Т")
            self.is_dark_theme = True

    def on_hotkey_change(self, choice):
        self.current_hotkey = choice
        if not self.is_running:
            self.toggle_btn.configure(text=f"СТАРТ ({self.current_hotkey})")

    def toggle_clicking(self):
        if self.is_running:
            self.stop_autoclicker()
        else:
            self.start_autoclicker()

    def play_sound(self, frequency, duration):
        threading.Thread(target=winsound.Beep, args=(frequency, duration), daemon=True).start()

    def start_autoclicker(self):
        try:
            self.interval = float(self.int_entry.get())
            if self.interval <= 0:
                raise ValueError
        except ValueError:
            self.interval = 1.0
            self.int_entry.delete(0, ctk.END)
            self.int_entry.insert(0, "1.0")

        try:
            self.start_delay = int(self.delay_entry.get())
            if self.start_delay < 0:
                raise ValueError
        except ValueError:
            self.start_delay = 0
            self.delay_entry.delete(0, ctk.END)
            self.delay_entry.insert(0, "0")

        self.current_hotkey = self.hk_var.get()
        self.mouse_button = self.btn_var.get()
        self.click_count = 0
        self.lbl_counter.configure(text="Кликов сделано: 0")
        self.is_running = True
        
        self.play_sound(1000, 250)

        self.int_entry.configure(state="disabled", fg_color=("#EAEAEA", "#222222"))
        self.delay_entry.configure(state="disabled", fg_color=("#EAEAEA", "#222222"))
        self.hk_menu.configure(state="disabled")
        self.btn_menu.configure(state="disabled")
        self.theme_btn.configure(state="disabled")
        self.toggle_btn.configure(fg_color=("#CCCCCC", "#555555"), hover_color=("#CCCCCC", "#555555"))

        threading.Thread(target=self.click_sequence, daemon=True).start()

    def stop_autoclicker(self):
        self.is_running = False
        self.play_sound(600, 300)

        self.current_hotkey = self.hk_var.get()
        self.toggle_btn.configure(text=f"СТАРТ ({self.current_hotkey})", fg_color=("#E0E0E0", "#404040"))
        self.int_entry.configure(state="normal", fg_color=("#F5F5F5", "#1A1A1A"))
        self.delay_entry.configure(state="normal", fg_color=("#F5F5F5", "#1A1A1A"))
        self.hk_menu.configure(state="readonly")
        self.btn_menu.configure(state="readonly")
        self.theme_btn.configure(state="normal")

    def click_sequence(self):
        current_delay = self.start_delay
        while current_delay > 0 and self.is_running:
            self.toggle_btn.configure(text=f"ЖДЕМ: {current_delay} сек")
            time.sleep(1)
            current_delay -= 1

        if not self.is_running:
            return

        if self.start_delay > 0:
            self.play_sound(2000, 200)

        self.toggle_btn.configure(text=f"СТОП ({self.current_hotkey})")
        btn = mouse.Button.left if self.mouse_button == "ЛКМ" else mouse.Button.right
        
        while self.is_running:
            self.mouse_controller.click(btn, 1)
            self.click_count += 1
            self.lbl_counter.configure(text=f"Кликов сделано: {self.click_count}")
            time.sleep(self.interval)

    def start_background_threads(self):
        def on_press(key):
            try:
                expected_key = getattr(keyboard.Key, self.current_hotkey.lower())
            except AttributeError:
                return

            if key == expected_key:
                self.root.after(0, self.toggle_clicking)

        self.kb_listener = keyboard.Listener(on_press=on_press)
        self.kb_listener.start()

    def on_closing(self):
        self.is_running = False
        if self.kb_listener:
            self.kb_listener.stop()
        self.root.destroy()
        sys.exit()

if __name__ == "__main__":
    root = ctk.CTk()
    app = AutoclickerApp(root)
    root.mainloop()
