import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

class InputValidator:
    def __init__(self, parent):
        self.parent = parent
        self.error_window = None

    def show_error(self, message):
        """Показывает всплывающее окно с сообщением об ошибке."""
        if self.error_window and self.error_window.winfo_exists():
            return  # Если окно уже открыто — не открываем новое

        self.error_window = tk.Toplevel(self.parent)
        self.error_window.overrideredirect(True)  # Убираем рамку
        self.error_window.geometry(f"+{self.parent.winfo_rootx()+10}+{self.parent.winfo_rooty()+30}")
        self.error_window.configure(bg="red")
        self.error_window.attributes("-topmost", True)

        label = ttk.Label(
            self.error_window,
            text=message,
            foreground="white",
            background="red",
            anchor="center"
        )
        label.pack(padx=10, pady=5)

        # Закрываем окно через 2 секунды
        self.error_window.after(2000, self.error_window.destroy)

    def validate_input(self, value):
        try:
            float(value.replace(",", "."))
            return True
        except ValueError:
            self.show_error("Ошибка: введите число")
            return False

# Пример использования
root = tk.Tk()
root.title("Валидация чисел")
root.geometry("300x200")

entry = ttk.Entry(root)
entry.pack(pady=10)

validator = InputValidator(root)

def on_validate(*args):
    value = entry.get()
    if not validator.validate_input(value):
        pass  # Обработка ошибки уже сделана внутри validate_input

entry_var = tk.StringVar()
entry_var.trace_add("write", on_validate)
entry.config(textvariable=entry_var)

root.mainloop()