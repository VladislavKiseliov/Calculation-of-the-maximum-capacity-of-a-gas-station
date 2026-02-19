import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from interfaces import MessageHandler_Interfaces

class MessageHandler(MessageHandler_Interfaces):

    def __init__(self,parent_window=None):
        self.parent_window = parent_window

    def show_success(self, message: str):
        """Показать сообщение об успехе"""
        messagebox.showinfo("Успех", message, parent=self.parent_window)

    def show_error(self, message: str):
        """Показать сообщение об ошибке"""
        messagebox.showerror("Ошибка", message, parent=self.parent_window)

    def show_warning(self, message: str):
        """Показать предупреждение"""
        messagebox.showwarning("Предупреждение", message, parent=self.parent_window)