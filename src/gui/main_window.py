"""
Main Window Module

This module contains the main window management classes:
- GuiManager: Manages the main application window and notebook tabs
- WidgetFactory: Factory for creating common GUI widgets
- CallbackRegistry: Event management system for GUI callbacks
"""

import tkinter as tk
from tkinter import FALSE, Menu, ttk
from typing import Dict


class WidgetFactory:
    """Factory class for creating common GUI widgets with consistent styling."""
    
    @staticmethod
    def create_entry(parent, row, column=1, padx=5, pady=5):
        """Create a standard entry widget."""
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=column, padx=padx, pady=pady)
        return entry

    @staticmethod
    def create_label(parent, label_text, row, column=0, padx=5, pady=5):
        """Create a standard label widget."""
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky="w")
        return label

    @staticmethod
    def create_Button(parent, label_text, row, function=None, column=0, padx=5, pady=5):
        """Create a standard button widget."""
        button = ttk.Button(parent, text=label_text, command=function)
        button.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
        return button


class CallbackRegistry:
    """Registry for managing GUI event callbacks in a decoupled way."""
    
    def __init__(self):
        self.callbacks = {}

    def register(self, event_name: str, callback):
        """Register a callback for a specific event."""
        self.callbacks[event_name] = callback

    def trigger(self, event_name, *args, **kwargs):
        """Trigger a callback for a specific event."""
        if event_name in self.callbacks:
            self.callbacks[event_name](*args, **kwargs)
        else:
            print(f"Колбэк для события '{event_name}' не зарегистрирован")


class GuiManager:
    """
    Main GUI window manager responsible for:
    - Creating and styling the main window
    - Managing the notebook tabs
    - Setting up the menu system
    - Providing access to tab frames
    """

    def __init__(self, root: tk.Tk, callback: CallbackRegistry):
        self.callback = callback
        self.root = root
        self.style = ttk.Style(root)
        self.tabs = {}
        
        self._setup_window()
        self._create_menu()
        self._create_style()
        self._create_notebook()

    def _setup_window(self):
        """Configure the main window properties."""
        self.root.title("Расчеты газовых систем")
        self.root.geometry("700x300")  # Starting window size
        self.root.minsize(700, 300)  # Minimum window size

    def get_tab_frame(self, tab_name: str) -> tk.Frame:
        """Get the frame for a specific tab."""
        return self.tabs[tab_name]

    def _create_menu(self):
        """Create the main application menu."""
        self.root.option_add("*tearOff", FALSE)

        main_menu = Menu()

        file_menu = Menu()
        file_menu.add_command(label="Save", command=lambda: self.callback.trigger("Save_file"))
        file_menu.add_command(label="Open", command=lambda: self.callback.trigger("Load_file"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit")

        main_menu.add_cascade(label="Файл", menu=file_menu)
        main_menu.add_cascade(label="Настройка")
        main_menu.add_cascade(label="Справка")
        self.root.config(menu=main_menu)

    def _create_style(self):
        """Configure the visual styling for the application."""
        # Configure tab styling
        self.style.configure(
            "TNotebook.Tab",
            background="#e0e0e0",  # Tab background color
            padding=[10, 5],  # Tab padding
            font=("Arial", 10, "bold"),
            borderwidth=0,  # No borders
            highlightthickness=0,  # No highlighting
        )

        # Configure active tab styling
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#d0d0d0")],
            expand=[("selected", [0, 0, 0, 0])],  # Remove border expansion
        )
        
        # Set overall theme and widget styles
        self.style.theme_use("clam")  # Modern theme
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure(
            "TButton", font=("Arial", 10, "bold"), padding=5, background="#4CAF50"
        )
        self.style.configure("Treeview", rowheight=25, font=("Arial", 10))

    def _create_notebook(self):
        """Create the main notebook widget with tabs."""
        # Create Notebook with custom styling
        self.notebook = ttk.Notebook(self.root, style="Custom.TNotebook")
        self.style.configure("Custom.TNotebook", tabposition="n", background="#e0e0e0")
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Configure grid weights for proper resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create tabs for different calculation sections
        tabs_name = [
            "Исходные данные",
            "Свойства газа", 
            "Расчет пропускной способности трубы",
            "Расчет регулятора",
            "Тепловой баланс",
        ]

        for name in tabs_name:
            frame = ttk.Frame(self.notebook)
            self.tabs[name] = frame  # Store frame in dictionary
            self.notebook.add(frame, text=name)