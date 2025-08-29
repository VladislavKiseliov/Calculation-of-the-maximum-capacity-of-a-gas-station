"""
Table Controller Module

This module contains the TableController class responsible for:
- Managing table creation and data loading
- Coordinating between GUI table components and data model
- Handling boiler data loading from files
- Managing table state and validation
"""

import logging
from tkinter import messagebox
from tkinter.messagebox import showinfo
from typing import Dict

from gui.Work_table import BaseTableManager, TableFactory


class TableController:
    """
    Controller class for managing table operations.
    
    Responsible for:
    - Creating and managing table instances
    - Coordinating between GUI table components and data model
    - Handling table data persistence
    - Managing special table types (like boiler data)
    """

    def __init__(self, guitable, callback, model):
        self.logger = logging.getLogger("App.TableController")
        self.callback = callback
        self.guitable = guitable
        self.model = model
        self.tables = {}
        
    def create_window_table(self, tables: Dict[str, BaseTableManager]):
        """Create table window with existing tables or empty window."""
        if not tables:
            self.guitable.create_window_table()
        else:
            self.guitable.create_window_table()
            for name in tables:
                self.guitable.creating_fields(tables[name].get_table_type(), name)

    def create_table(self, table_name, table_type):
        """Create a new table with specified name and type."""
        if table_name == "":
            messagebox.showwarning("Ошибка", "Введите название таблицы")
            return

        if table_name in self.tables:
            self.logger.warning(f"Таблица '{table_name}' уже существует")
            messagebox.showwarning("Ошибка", f"Таблица '{table_name}' уже существует!")
            return
        
        # Create table manager using factory pattern
        manager = TableFactory.create_table_manager(table_type)
        self.tables[table_name] = manager
        data = {table_name: manager}
        self.model.save_table(data)
   
    def open_table(self, table_name, table_type):
        """Open existing table or create new one if doesn't exist."""
        if table_name not in self.tables:
            self.create_table(table_name, table_type)

        if table_type == "Таблица котельной":
            self.load_boiler_data()
        else:
            data = self.model.get_table_data(table_name)[0]
            self.guitable.open_table_window(
                table_name, 
                self.tables[table_name].get_columns(), 
                data
            )
 
    def save_table(self):
        """Save table data to the database."""
        table_data = self.guitable.get_data_table() 
        table_name, values = next(iter(table_data.items()))
        columns = self.tables[table_name].get_columns() 
        data = dict(zip(columns, values))
        self.model.create_db_table(
            table_name, 
            self.tables[table_name].get_table_type(), 
            data
        )
        self.guitable.window_table.destroy()

    def load_boiler_data(self):
        """Load boiler data from external file with comprehensive error handling."""
        try:
            self.model.load_boiler_data()
            self.logger.info("Все данные успешно обработаны и сохранены")
            showinfo("Успех", "Данные котельной успешно загружены и обработаны!")
            
        except FileNotFoundError:
            messagebox.showerror("Ошибка", "Выбранный файл не найден")
            return
        except KeyError as e:
            messagebox.showerror("Ошибка", f"В файле отсутствует необходимый столбец: {e}")
            return
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка при загрузке данных: {str(e)}")
            return