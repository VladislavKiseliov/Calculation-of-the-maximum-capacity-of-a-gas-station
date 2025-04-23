import csv
import logging
import os
import sqlite3
import tkinter as ttk
from tkinter import filedialog
from tkinter.messagebox import showinfo, showwarning
from typing import Any, Dict, List, Optional, TypedDict

import numpy as np
import pandas as pd

import logger_config


class Data_model:
    """Stores and manages application data.
    This class provides a centralized location for storing and retrieving
    various data used in the application, such as gas composition,
    pressure ranges, table data, and gas properties.
    """
    def __init__(self):
        self.logger = logging.getLogger("App.DataModel")  # Дочерний логгер
        self.gas_composition = {}
        self.input_pressure_range = []
        self.output_pressure_range = None
        self.tables_data = {}
        self.gas_properties = {}
        self._temperature = {}
        self.db_path = "tables.db"
    
    @property
    def data_gas_composition(self)-> Dict[str,float] :
        return self.gas_composition
    
    @data_gas_composition.setter
    def data_gas_composition(self, composition: Dict[str,str]):
        # Сохраняем введенные данные
        total_percentage = 0.0
        self.gas_composition = {} #Очищаем словарь, что бы не накладывало значения
        for component, percentage in composition.items():
            try:
                percentage = float(percentage)
                if percentage < 0:
                    raise ValueError("Отрицательное значение")
                self.gas_composition[component] = percentage
                total_percentage += percentage
            except ValueError:
                self.gas_composition[component] = 0.0  # Если введено неверное значение, считаем 0%

        # Проверяем, что сумма процентов равна 100%
        if abs(total_percentage - 100.0) > 0.001:  # Допускаем небольшую погрешность
            print(f"{abs(total_percentage - 100.0)=}")
            self.logger.error("Ошибка", f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.4f}%")
            showwarning("Ошибка", f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.4f}%")
            return 

        else:
            showinfo("Успех", "Данные успешно сохранены!")
            self.logger.info("Состав газа сохранен")
            print(self.gas_composition)
           
    def set_gas_composition_from_file(self, loaded_composition): #Скорее всего убрать
        """
        Sets the gas composition from a loaded dictionary.

        Args:
            loaded_composition (dict): The dictionary of loaded gas composition data.
        """
        self.gas_composition = loaded_composition
        self.logger.info(f"Состав газа установлен из файла: {self.gas_composition}")
        print(f"Состав газа установлен из файла: {self.gas_composition}")    
    
    def get_input_pressure_range(self)-> List[float]:
        return self.input_pressure_range

    def get_output_pressure_range(self)-> List[float]:
        return self.output_pressure_range

    def set_pressure_range(self, pressure_type:str,pressure_range:List[float]):
        """
        Устанавливает диапазон давлений (входного или выходного).
        :param pressure_type: "input" для входного давления, "output" для выходного.
        """
        try:
        # Если диапазон не сгенерирован (ошибка), прерываем выполнение
            if pressure_range is None:
                self.logger.error(f"Диапазон {pressure_type} давлений не был сгенерирован")
                return  # Не закрываем окно и не выводим сообщение
            
            # Если всё успешно
            setattr(self, f"{pressure_type}_pressure_range", pressure_range)
            self.logger.info(f"Данные диапазона {pressure_type} давления сохранены")

            print(getattr(self, f"{pressure_type}_pressure_range"))
            showinfo("Успех", "Данные успешно сохранены!")
            # window.destroy()  # Закрываем окно

        except Exception as e:
            self.logger.error(f"Не удалось сохранить данные: {e}")
            showwarning("Ошибка", f"Не удалось сохранить данные: {e}")

    def get_table_manager(self)->List[Dict[str, Any]]:
        """Возвращаем название и тип таблиц"""
        return self.tables_data

    def get_data_table(self,name_table) -> List[Dict[str, Any]]: 
        """Получение данных из базы данных."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {name_table}", conn)
            self.logger.info(f"Данные таблицы {name_table} полученны из баззы данных")
        return df.to_dict(orient="records")[0]  # Список словарей

    def set_tables_data(self, tables: Dict[str,Any]):
        self.tables_data = tables
        print(self.tables_data)
        for i in self.tables_data:
            print(f"{self.tables_data[i].get_table_type()=}")
        self.logger.info(f"Данные таблицы {self.tables_data} добавлены в Data_model")
    
    def get_gas_properties(self):
        return self.gas_properties

    def set_gas_properties(self, gas_properties):
        self.gas_properties = gas_properties
        self.logger.info(f"Данные свойств газа {self.gas_properties} сохранены в Data_model")

    @property
    def temperature(self)-> Dict[str,float]:
        return self._temperature
    
    @temperature.setter
    def temperature(self,temp:float):
        print(temp)
        self._temperature = {"in":temp[0],"out":temp[1]}
        self.logger.info(f"Данные температуры газа {self._temperature} сохранены в Data_model")


class CSVManager:
    def __init__(self):
        self.logger = logging.getLogger("App.CSVManager")  # Дочерний логгер

    def save_gas_composition_to_csv(self,gas_composition:Dict[str,float]):
        """Saves the current gas composition to a CSV file."""
        try:
            # Открываем проводник для выбора пути и имени файла
            file_path = filedialog.asksaveasfilename(
                title="Сохранить состав газа как",
                defaultextension=".csv",  # Расширение по умолчанию
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]  # Фильтр типов файлов
            )

            if not file_path:  # Если пользователь отменил выбор
                self.logger.warning("Отмена.Сохранение отменено пользователем")
                showwarning("Отмена", "Сохранение отменено пользователем")
                return

            # Сохраняем данные в выбранный файл
            with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Component", "Percentage"])  # Заголовок таблицы

                for component, percentage in gas_composition.items():
                        writer.writerow([component, percentage])
          
            # Уведомляем пользователя об успешном сохранении
            self.logger.info(f"Состав газа сохранен в файл: {file_path}")
            showinfo("Успех", f"Состав газа сохранен в файл: {file_path}")
        except Exception as e:
            self.logger.error("Ошибка", f"Не удалось сохранить в файл: {e}")
            # Обрабатываем ошибки при сохранении
            showwarning("Ошибка", f"Не удалось сохранить в файл: {e}")

    def load_gas_composition_from_csv(self)-> Dict[str,float]:
        """Loads the gas composition from a CSV file """
        try:
            # Открываем проводник для выбора файла
            file_path = filedialog.askopenfilename(
                title="Выберите файл для загрузки состава газа",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]  # Фильтр типов файлов
            )

            if not file_path:  # Если пользователь отменил выбор
                showwarning("Отмена", "Загрузка отменена пользователем")
                self.logger.warning("Отмена", "Загрузка отменена пользователем")
                return

            # Проверяем существование файла
            if not os.path.exists(file_path):
                showwarning("Ошибка", f"Файл {file_path} не найден.")
                self.logger.error("Ошибка", f"Файл {file_path} не найден.")
                return

            # Загружаем данные из выбранного файла
            with open(file_path, mode='r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                loaded_composition = {}
                for row in reader:
                    try:
                        loaded_composition[row["Component"]] = float(row["Percentage"])
                    except ValueError:
                        loaded_composition[row["Component"]] = 0.0  # Если значение некорректно, записываем 0.0
                        self.logger.warning(f"{loaded_composition[row["Component"]]} = 0.0")

                # Устанавливаем состав газа в модели и обновляем поля ввода
                return loaded_composition
                
            # Уведомляем пользователя об успешной загрузке
            showinfo("Успех", f"Состав газа загружен из файла: {file_path}")
            self.logger.info(f"Состав газа загружен из файла: {file_path}")

        except Exception as e:
            # Обрабатываем ошибки при загрузке
            self.logger.error("Ошибка", f"Не удалось загрузить из файла: {e}")
            showwarning("Ошибка", f"Не удалось загрузить из файла: {e}")

class DataBaseManager:
    def __init__(self):
        self.logger = logging.getLogger("App.DataBaseManager")  # Дочерний логгер

    def create_table_query(self,colums:List[str],table_name:str) -> str:
        """Create a request to create a table in the database"""
        # Проверяем, что колонки не пустые
        if not colums:
            self.logger.error("Список колонок пуст!")
            raise ValueError("Колонки не определены") 
        # Формируем SQL-запрос для создания таблицы
        create_table_query = f'''
            CREATE TABLE IF NOT EXISTS '{table_name}' (
                {", ".join([f"{col} REAL" for col in colums])}
            )
        '''
        self.logger.debug(f"SQL-запрос создания таблицы: {create_table_query}")

    def insert_query(self,colums:List[str],table_name:str) -> str:
        """Create a request to insert data into the table"""
        insert_query = f'''
            INSERT INTO '{table_name}' ({", ".join(colums)}) 
            VALUES ({", ".join(["?"] * len(colums))})
        '''
        self.logger.debug(f"SQL-запрос вставки данных: {insert_query}")
        

class JsonManager:
    def __init__(self):
        self.logger = logging.getLogger("App.JsonManager")  # Дочерний логгер