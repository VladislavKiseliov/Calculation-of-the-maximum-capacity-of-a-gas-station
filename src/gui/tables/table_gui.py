"""
Table GUI Module

This module contains the GuiTable class responsible for:
- Creating and managing table input dialogs
- Handling table data display and editing
- Managing table selection interface
- Providing table data access for controllers
"""

import logging
import tkinter as tk
from tkinter import messagebox, ttk
from typing import Dict, List

from ..main_window import WidgetFactory


class GuiTable:
    """
    GUI component for managing table interfaces.
    
    Responsible for:
    - Creating table selection and input dialogs
    - Managing table data display in Treeview widgets
    - Handling table editing functionality
    - Providing data access methods for controllers
    """

    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.row = 3
        self.tables = {}  # Store opened table references
        self.table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной", 
            "Таблицы для труб до регулятора",
            "Таблицы для труб после регулятора",
        ]
        self.logger = logging.getLogger("App.GuiTable")
        
    def create_window_table(self):
        """Create the main table management window."""
        self.table_window = tk.Toplevel(self.parent)
        self.table_window.title("Таблицы граничных условий")

        # Table type selection label
        label = WidgetFactory.create_label(self.table_window, "Выберите таблицу:", 0)

        # Table type combobox
        self.combobox = ttk.Combobox(
            self.table_window, values=self.table_labels, state="readonly", width=33
        )
        self.combobox.grid(row=1, column=0, padx=5, pady=5)

        # Add table button
        self.add_table_button = WidgetFactory.create_Button(
            parent=self.table_window,
            label_text="Добавить таблицу",
            row=2,
            function=self.add_table
        )
    
    def add_table(self):
        """Add a new table entry to the interface."""
        self.selection = self.combobox.get()
        if not self.selection:
            self.logger.error("Тип таблицы не выбран")
            messagebox.showwarning("Ошибка", "Тип таблицы не выбран!")
            return
        self.row += 1
        self.creating_fields(self.selection)

    def creating_fields(self, table_type, table_name=None):
        """Create input fields for a specific table type."""
        # Table type label
        type_label = WidgetFactory.create_label(
            self.table_window, label_text=table_type, row=self.row
        )
        
        # Table name input field
        self.entry_name_table = WidgetFactory.create_entry(
            self.table_window, self.row, 1
        )
        if table_name:
            self.entry_name_table.insert(0, table_name)

        # Open table button
        self.open_button = WidgetFactory.create_Button(
            self.table_window,
            "Открыть таблицу",
            self.row,
            lambda e=self.entry_name_table: self.callback.trigger(
                "open_table", 
                table_name=e.get(), 
                table_type=table_type
            ),
            3
        )
        self.row += 1 

    def open_table_window(self, table_name: str, columns: list, data: Dict[str, float]):
        """Open a table editing window with data."""
        self.table_name = table_name
        self.logger.info(f"Открытие окна таблицы '{self.table_name}'")

        # Prepare initial data
        if data is not None:
            init_data = list(data.values())
        else:
            init_data = ["-"] * len(columns)

        self.logger.debug(f"Данные для инициализации: {data}")
        
        try:
            # Create table window
            self.window_table = tk.Toplevel(self.parent)
            self.window_table.title(f"Таблица: {self.table_name}")
            self.logger.debug(f"Создано новое окно для таблицы '{self.table_name}'")

            # Create Treeview widget
            self.tree = ttk.Treeview(self.window_table, columns=columns, show="headings")
            for col in columns:
                self.tree.heading(col, text=col)
            self.tree.insert("", "end", values=init_data)
            self.tree.grid(row=0, column=0, sticky="nsew")
            self.logger.debug("Treeview инициализирован с колонками")

            # Configure grid weights for proper resizing
            self.window_table.grid_rowconfigure(0, weight=1)
            self.window_table.grid_columnconfigure(0, weight=1)

            # Save data button
            self.save_data_button = ttk.Button(
                self.window_table, 
                text="Сохранить данные",
                command=lambda: self.callback.trigger("save_table")
            )
            self.save_data_button.grid(row=1, column=0, pady=10, sticky="ew")
            self.logger.debug("Кнопка сохранения добавлена в окно")

            # Enable cell editing on double-click
            self.tree.bind("<Double-1>", self._add_editing_features)
            self.logger.debug("Событие двойного клика привязано к редактированию ячеек")

        except Exception as e:
            self.logger.exception(f"Ошибка при открытии окна таблицы '{self.table_name}'")
            messagebox.showerror("Ошибка", f"Не удалось открыть таблицу: {e}")

    def _add_editing_features(self, event):
        """Handle double-click for cell editing."""
        # Check if click is on a cell
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
            
        # Get row ID and column
        item_id = self.tree.focus()
        column = self.tree.identify_column(event.x)
        column_index = int(column[1:]) - 1  # Column index (starting from 0)

        # Get current cell value
        current_value = self.tree.item(item_id)["values"][column_index]

        # Create Entry widget for editing
        entry = ttk.Entry(self.tree)
        entry.insert(0, str(current_value))
        entry.focus()

        # Position Entry over the cell
        x, y, width, height = self.tree.bbox(item_id, column)
        entry.place(x=x, y=y, width=width, height=height)

        # Handle edit completion
        def save_edit(event=None):
            new_value = entry.get()
            values = list(self.tree.item(item_id)["values"])
            values[column_index] = new_value
            self.tree.item(item_id, values=values)
            entry.destroy()

        entry.bind("<Return>", save_edit)  # Save on Enter
        entry.bind("<FocusOut>", save_edit)  # Save on focus loss

    def get_data_table(self) -> Dict[str, List]:
        """Get current table data as dictionary."""
        table_data = [self.tree.item(item)["values"] for item in self.tree.get_children()][0]
        self.logger.debug(f"Получены данные таблицы: {table_data}")
        
        return {
            self.table_name: table_data
        }