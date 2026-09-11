import tkinter as tk

class Notifier:
    app_instance = None

    @classmethod
    def set_app(cls, app):
        cls.app_instance = app

    @classmethod
    def show_success(cls):
        if cls.app_instance:
            cls.app_instance.after(0, lambda: cls._create_overlay("✅", "green"))

    @classmethod
    def show_error(cls):
        if cls.app_instance:
            cls.app_instance.after(0, lambda: cls._create_overlay("❌", "red"))

    @classmethod
    def _create_overlay(cls, symbol, color):
        overlay = tk.Toplevel(cls.app_instance)
        overlay.overrideredirect(True)
        overlay.geometry("+20+20")
        overlay.attributes("-topmost", True)

        try:
            overlay.attributes("-transparentcolor", "white")
        except tk.TclError:
            pass

        overlay.configure(bg="white")
        overlay.attributes("-alpha", 0.9)

        label = tk.Label(overlay, text=symbol, font=("Arial", 36), fg=color, bg="white")
        label.pack()

        cls.app_instance.after(1500, lambda: cls._fade_out(overlay, 90))

    @classmethod
    def _fade_out(cls, window, alpha):
        if not window.winfo_exists():
            return

        if alpha <= 0:
            window.destroy()
        else:
            window.attributes("-alpha", alpha / 100.0)
            cls.app_instance.after(50, lambda: cls._fade_out(window, alpha - 10))
