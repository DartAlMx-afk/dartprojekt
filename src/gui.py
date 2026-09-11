import customtkinter as ctk
import sys
import tkinter.messagebox as messagebox
import threading
from .logger import logger
from .config import config_manager
from .hotkeys import hotkey_manager
from .ai_client import ai_client
from .notifier import Notifier

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

try:
    import pywinstyles
    HAS_WINSTYLES = True
except ImportError:
    HAS_WINSTYLES = False
    logger.warning("pywinstyles not found. Glass effects disabled.")

class AdvancedSettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Настройки")
        self.geometry("450x550")
        self.parent = parent

        self.attributes("-topmost", True)
        self.grid_columnconfigure(0, weight=1)

        if HAS_WINSTYLES:
            pywinstyles.apply_style(self, "acrylic")

        self.title_label = ctk.CTkLabel(self, text="Расширенные настройки", font=ctk.CTkFont(size=18, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(15, 10))

        self.hotkey_label = ctk.CTkLabel(self, text="Горячая клавиша:")
        self.hotkey_label.grid(row=1, column=0, padx=20, pady=(10, 0), sticky="w")
        self.hotkey_entry = ctk.CTkEntry(self, border_width=1, corner_radius=5)
        self.hotkey_entry.insert(0, config_manager.get("hotkey"))
        self.hotkey_entry.grid(row=2, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.temp_label = ctk.CTkLabel(self, text="Температура ИИ (0.0 - 1.0):")
        self.temp_label.grid(row=3, column=0, padx=20, pady=(10, 0), sticky="w")
        self.temp_entry = ctk.CTkEntry(self, border_width=1, corner_radius=5)
        self.temp_entry.insert(0, str(config_manager.get("temperature")))
        self.temp_entry.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.prompt_label = ctk.CTkLabel(self, text="Промпт (Инструкция):")
        self.prompt_label.grid(row=5, column=0, padx=20, pady=(10, 0), sticky="w")
        self.prompt_textbox = ctk.CTkTextbox(self, height=120, border_width=1, corner_radius=5)
        self.prompt_textbox.insert("0.0", config_manager.get("system_prompt"))
        self.prompt_textbox.grid(row=6, column=0, padx=20, pady=(5, 10), sticky="ew")

        self.delays_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.delays_frame.grid(row=7, column=0, padx=20, pady=10, sticky="ew")
        self.delays_frame.grid_columnconfigure(0, weight=1)
        self.delays_frame.grid_columnconfigure(1, weight=1)

        self.cdelay_label = ctk.CTkLabel(self.delays_frame, text="Пауза копирования (сек):")
        self.cdelay_label.grid(row=0, column=0, padx=5, pady=(5, 0))
        self.cdelay_entry = ctk.CTkEntry(self.delays_frame, border_width=1, corner_radius=5)
        self.cdelay_entry.insert(0, str(config_manager.get("copy_delay")))
        self.cdelay_entry.grid(row=1, column=0, padx=5, pady=(0, 5))

        self.pdelay_label = ctk.CTkLabel(self.delays_frame, text="Пауза вставки (сек):")
        self.pdelay_label.grid(row=0, column=1, padx=5, pady=(5, 0))
        self.pdelay_entry = ctk.CTkEntry(self.delays_frame, border_width=1, corner_radius=5)
        self.pdelay_entry.insert(0, str(config_manager.get("paste_delay")))
        self.pdelay_entry.grid(row=1, column=1, padx=5, pady=(0, 5))

        self.autostart_var = ctk.BooleanVar(value=config_manager.get("autostart"))
        self.autostart_checkbox = ctk.CTkCheckBox(self, text="Автозагрузка с Windows", variable=self.autostart_var)
        self.autostart_checkbox.grid(row=8, column=0, padx=20, pady=(10, 0), sticky="w")

        self.save_button = ctk.CTkButton(self, text="Применить", command=self.save_and_close, fg_color="gray20", hover_color="gray30", border_width=1, border_color="gray40")
        self.save_button.grid(row=9, column=0, padx=20, pady=20, sticky="ew")

        self.protocol("WM_DELETE_WINDOW", self.save_and_close)

    def save_and_close(self):
        try:
            config_manager.set("hotkey", self.hotkey_entry.get().strip())
            config_manager.set("temperature", float(self.temp_entry.get().strip()))
            config_manager.set("system_prompt", self.prompt_textbox.get("0.0", "end").strip())
            config_manager.set("copy_delay", float(self.cdelay_entry.get().strip()))
            config_manager.set("paste_delay", float(self.pdelay_entry.get().strip()))

            enable_autostart = self.autostart_var.get()
            config_manager.set("autostart", enable_autostart)
            from .autostart import setup_autostart
            setup_autostart(enable_autostart)

            config_manager.save()
            logger.info("Advanced settings updated.")

            if not hotkey_manager.is_running:
                hotkey = config_manager.get("hotkey").upper()
                self.parent.toggle_button.configure(text=f"ЗАПУСТИТЬ ({hotkey})")

            self.destroy()
        except ValueError:
            messagebox.showerror("Ошибка", "Пожалуйста, введите числа для температуры и задержек.")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("AI Text Corrector")
        self.geometry("500x600")

        if HAS_WINSTYLES:
            pywinstyles.apply_style(self, "acrylic")

        Notifier.set_app(self)
        hotkey_manager.status_callback = self.update_status_ui

        self.setup_ui()
        logger.info("GUI initialized.")

        self.after(500, self.auto_check_system)

    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)

        self.title_label = ctk.CTkLabel(self, text="AI TEXT CORRECTOR", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.grid(row=0, column=0, padx=20, pady=(30, 20))

        self.backend_var = ctk.StringVar(value=config_manager.get("backend"))

        self.backend_option = ctk.CTkSegmentedButton(self, values=["Ollama", "LM Studio", "Local GGUF"], variable=self.backend_var, command=self.on_backend_change)
        self.backend_option.grid(row=1, column=0, padx=40, pady=(5, 20), sticky="ew")

        self.config_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.config_frame.grid(row=2, column=0, padx=40, pady=5, sticky="ew")
        self.config_frame.grid_columnconfigure(0, weight=1)

        self.url_label = ctk.CTkLabel(self.config_frame, text="URL Сервера:", text_color="gray70")
        self.url_label.grid(row=0, column=0, pady=(5, 0), sticky="w")
        self.url_entry = ctk.CTkEntry(self.config_frame, border_width=1, corner_radius=5)
        self.url_entry.grid(row=1, column=0, pady=(0, 15), sticky="ew")

        self.model_label = ctk.CTkLabel(self.config_frame, text="Название модели:", text_color="gray70")
        self.model_label.grid(row=2, column=0, pady=(5, 0), sticky="w")

        self.model_entry_frame = ctk.CTkFrame(self.config_frame, fg_color="transparent")
        self.model_entry_frame.grid(row=3, column=0, pady=(0, 15), sticky="ew")
        self.model_entry_frame.grid_columnconfigure(0, weight=1)

        self.model_entry = ctk.CTkEntry(self.model_entry_frame, border_width=1, corner_radius=5)
        self.model_entry.grid(row=0, column=0, sticky="ew")

        self.browse_button = ctk.CTkButton(self.model_entry_frame, text="Обзор", width=60, command=self.browse_gguf)
        self.browse_button.grid(row=0, column=1, padx=(5, 0))

        self.on_backend_change(config_manager.get("backend"))

        self.adv_settings_button = ctk.CTkButton(self, text="⚙️ Дополнительные настройки", command=self.open_advanced_settings, fg_color="transparent", border_width=1, text_color="gray80", hover_color="gray20")
        self.adv_settings_button.grid(row=3, column=0, padx=40, pady=10, sticky="ew")

        self.status_label = ctk.CTkLabel(self, text="● Инициализация...", text_color="gray50", font=ctk.CTkFont(size=14))
        self.status_label.grid(row=4, column=0, padx=20, pady=(30, 5))

        current_hotkey = config_manager.get("hotkey").upper()
        self.toggle_button = ctk.CTkButton(self, text=f"ЗАПУСТИТЬ ({current_hotkey})", command=self.toggle_tracking, height=45, font=ctk.CTkFont(size=14, weight="bold"), fg_color="gray20", hover_color="gray30", border_width=1, border_color="gray50")
        self.toggle_button.grid(row=5, column=0, padx=40, pady=10, sticky="ew")


    def on_backend_change(self, choice):
        self.url_entry.configure(state="normal")
        self.url_entry.delete(0, "end")
        self.model_entry.delete(0, "end")

        if choice == "Ollama":
            self.url_entry.insert(0, config_manager.get("ollama_url"))
            self.model_entry.insert(0, config_manager.get("ollama_model"))
            self.browse_button.grid_remove()
            self.model_label.configure(text="Название модели:")
        elif choice == "LM Studio":
            self.url_entry.configure(state="normal")
            self.url_entry.insert(0, config_manager.get("lmstudio_url"))
            self.model_entry.insert(0, config_manager.get("lmstudio_model"))
            self.browse_button.grid_remove()
            self.model_label.configure(text="Название модели:")
        elif choice == "Local GGUF":
            self.url_entry.insert(0, "Локальный файл (URL не требуется)")
            self.url_entry.configure(state="disabled")
            self.model_entry.insert(0, config_manager.get("gguf_model_path"))
            self.browse_button.grid()
            self.model_label.configure(text="Путь к файлу .gguf:")
            from .ai_client import ai_client
            ai_client.load_gguf_model(config_manager.get("gguf_model_path"))

    def browse_gguf(self):
        from customtkinter import filedialog
        filename = filedialog.askopenfilename(
            title="Выберите GGUF файл",
            filetypes=[("GGUF Files", "*.gguf"), ("All Files", "*.*")]
        )
        if filename:
            self.model_entry.delete(0, "end")
            self.model_entry.insert(0, filename)
            config_manager.set("gguf_model_path", filename)
            config_manager.save()
            from .ai_client import ai_client
            ai_client.load_gguf_model(filename)

    def save_settings(self):
        backend = self.backend_var.get()
        config_manager.set("backend", backend)

        if backend == "Ollama":
            config_manager.set("ollama_url", self.url_entry.get().strip())
            config_manager.set("ollama_model", self.model_entry.get().strip())
        elif backend == "LM Studio":
            config_manager.set("lmstudio_url", self.url_entry.get().strip())
            config_manager.set("lmstudio_model", self.model_entry.get().strip())
        elif backend == "Local GGUF":
            config_manager.set("gguf_model_path", self.model_entry.get().strip())

        config_manager.save()
        logger.info("Main settings updated via GUI.")

    def auto_check_system(self):
        def check_task():
            self.after(0, lambda: self.status_label.configure(text="● Проверка соединения с ИИ...", text_color="yellow"))
            success, message = ai_client.test_connection()
            if success:
                self.after(0, lambda: self.status_label.configure(text="● Готов к работе", text_color="#00FF00"))
            else:
                self.after(0, lambda: self.status_label.configure(text="● Ошибка: ИИ недоступен", text_color="#FF4444"))

        threading.Thread(target=check_task, daemon=True).start()

    def open_advanced_settings(self):
        AdvancedSettingsWindow(self)

    def toggle_tracking(self):
        self.save_settings()
        hotkey_manager.toggle_tracking()

    def update_status_ui(self, is_running):
        current_hotkey = config_manager.get("hotkey").upper()
        if is_running:
            self.toggle_button.configure(text=f"ОСТАНОВИТЬ", fg_color="#330000", hover_color="#550000", border_color="#FF4444")
            self.status_label.configure(text=f"● Отслеживание ({current_hotkey})", text_color="#00FF00")
        else:
            self.toggle_button.configure(text=f"ЗАПУСТИТЬ ({current_hotkey})", fg_color="gray20", hover_color="gray30", border_color="gray50")
            self.status_label.configure(text="● Приостановлено", text_color="gray50")

    def on_closing(self):
        logger.info("Closing application...")
        self.save_settings()
        hotkey_manager.stop_tracking()
        self.destroy()
        sys.exit(0)

def run_app():
    app = App()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
