import base64
import csv
import json
import logging
import os
import sqlite3
import tkinter as ttk
from tkinter import filedialog, messagebox
from tkinter.messagebox import showinfo, showwarning
from typing import Any, Dict, List
import pickle

import numpy as np
import pandas as pd

from Work_table import BaseTableManager


class Data_model:
    """Stores and manages application data.
    This class provides a centralized location for storing and retrieving
    various data used in the application, such as gas composition,
    pressure ranges, table data, and gas properties.
    """

    def __init__(self, data_storage : "DataStorage", csvmanager:"CSVManager", data_base :"DataBaseManager", json_manager:"JsonManager"):
        
        self.logger = logging.getLogger("App.DataModel")  # Дочерний логгер
        self.data_storage = data_storage
        self.csv_manager = csvmanager
        self.data_base_manager = data_base
        self.json_manager = json_manager
        self.saves_dir = "Saves"

    # Раюота с давлением
    def _calculate_pressure_range(
        self, min_pressure:float,max_pressure:float,step:float) -> List[float]:
        try:
            # Проверка корректности данных
            if min_pressure > max_pressure:
                raise ValueError("Ошибка: Минимальное давление больше максимального.")
            if step <= 0:
                raise ValueError("Ошибка: Шаг должен быть положительным числом.")

            pressure_range = np.arange(
                min_pressure, max_pressure + step, step
            ).tolist()
            return [round(p, 1) for p in pressure_range]

        except ValueError as e:
            # Вывод ошибки
            showwarning("Ошибка", e)
            return

    def save_pressure_range1(self, title: str, min_pressure:float,max_pressure:float,step:float):
        """
        Сохраняет диапазон давлений.
        """
        if not all([min_pressure, max_pressure, step]):
            raise ValueError("Ошибка: Введите значения")
        try:
            pressure_type = title.lower()
            set_pressure_range = self._calculate_pressure_range(
                min_pressure, max_pressure, step
            )
            
            self.data_storage.set_pressure_range(pressure_type, set_pressure_range)

            self.logger.info(
                f"Диапазоны {pressure_type} давления  успешно сохранены: максимальное = %s мПа, минимальное = %s мПа,шаг = %s",
                max_pressure,
                min_pressure,
                step,
            )
        except ValueError:
            self.logger.warning("Введите корректные числовые значения!")
            showwarning("Ошибка", "Введите корректные числовые значения!")

    def get_pressure_range(self, title: str) -> List[float]:
        """
        Получает диапазон давлений.
        """
        pressure_type = title.lower()
        return (
            self.data_storage.get_input_pressure_range()
            if pressure_type == "input"
            else self.data_storage.get_output_pressure_range()
        )

    # Работа с составом газа
    def load_gas_composition(self)-> Dict[str, float]:
        """Loads the gas composition from the data model and updates the entry fields."""
        return self.data_storage.data_gas_composition

    def validate_gaz_composition(self, composition: Dict[str, str]) -> Dict[str, float]:
        total_percentage = 0.0
        gas_composition = {}  # Очищаем словарь, что бы не накладывало значения
        for component, percentage in composition.items():
            try:
                percentage = float(percentage)
                if percentage < 0:
                    raise ValueError("Отрицательное значение")
                gas_composition[component] = percentage
                total_percentage += percentage
            except ValueError:
                gas_composition[component] = (
                    0.0  # Если введено неверное значение, считаем 0%
                )

        # Проверяем, что сумма процентов равна 100%
        if abs(total_percentage - 100.0) > 0.001:  # Допускаем небольшую погрешность
            print(f"{abs(total_percentage - 100.0)=}")
            self.logger.error(
                "Ошибка",
                f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.4f}%",
            )
            showwarning(
                "Ошибка",
                f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.4f}%",
            )
            return
        return gas_composition

    def save_sostav_gaz(self,  composition: Dict[str, str]):
        gas_composition = self.validate_gaz_composition(composition)
        self.data_storage.data_gas_composition = gas_composition

    def save_gaz_to_csv(self, composition: Dict[str, str]):  # Исправить на класс работы с csv
        gas_composition = self.validate_gaz_composition(composition)
        self.csv_manager.save_gas_composition_to_csv(gas_composition)

    def load_gaz_from_csv(self):  # Исправить на класс работы с csv
        return self.csv_manager.load_gas_composition_from_csv()

    # Работа с температурной
    def save_temp(self, data):
        self.logger.info(
            f"Данные температуры газа {self.data_storage.temperature} сохранены в Data_model"
        )
        print(data)
        self.data_storage.temperature = data
        print(self.data_storage.temperature)

    def get_temperature(self) -> Dict[str, float]:
        return self.data_storage.temperature

    # Работа с исходными таблицами
    def get_table_manager(self) -> Dict[str, BaseTableManager]:
        """def get_table_manager(self)-> Dict[str, BaseTableManager]"""
        return self.data_storage.table_manager

    def create_db_table(self,table_name : str,table_type:str, parametr_table : Dict[str,float]):
        """Adding source data to the table"""
        try:
            self.data_base_manager.add_initial_table(table_name,table_type, parametr_table)
            showinfo("Успех", "Таблица успешно сохранена")
        except Exception as e:
            self.logger.exception(
                f"Неожиданная ошибка при добавлении таблицы '{table_name}' в базу данных"
            )
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
  
    def get_table_data(self, table_name) -> Dict[str, float]:
         return self.data_base_manager.load_data(table_name)

    def save_table(self,data):
        self.data_storage.table_manager.update(data)
    
    def save_intermedia(self,df,P_out):
        self.data_base_manager.save(df,P_out)

    # Сохранение/загрузка конфигурации расчета 
    def export_config(self):

        tables = self.get_table_manager()
        table_data = {}

        for table_name in tables:
            print(tables[table_name])
            serialized_manager = pickle.dumps(tables[table_name])
            encoded_manager = base64.b64encode(serialized_manager).decode('ascii')
            print(serialized_manager)
            data =self.get_table_data(table_name)
            table_data[table_name]=[encoded_manager,data]

        file = {
                    "gas_composition": self.load_gas_composition(),
                    "input_pressure_range": self.get_pressure_range("input"),
                    "output_pressure_range": self.get_pressure_range("output"),
                    "temperature": self.get_temperature(),
                    "table_name": table_data
                }
        self.json_manager.save_configure(file)
        
    def import_config(self):

        data = self.json_manager.load_data()
        self.save_sostav_gaz(data["gas_composition"])
        self.save_temp(data["temperature"])
        self.data_storage.set_pressure_range("input",data["input_pressure_range"])
        self.data_storage.set_pressure_range("output",data["output_pressure_range"])
        for table_name in data["table_name"]:
            encoded_manager = data["table_name"][table_name][0]
            serialized_manager = base64.b64decode(encoded_manager.encode('ascii'))
            table_manager = pickle.loads(serialized_manager)
            self.data_storage.table_manager[table_name] = table_manager
            self.create_db_table(table_name,table_manager.get_table_type(),data["table_name"][table_name][1])
            
class CSVManager:
    """Работа с файлами типа CSV"""

    def __init__(self):
        self.logger = logging.getLogger("App.CSVManager")  # Дочерний логгер

    def save_gas_composition_to_csv(self, gas_composition: Dict[str, float]):
        """Saves the current gas composition to a CSV file."""
        try:
            # Открываем проводник для выбора пути и имени файла
            file_path = filedialog.asksaveasfilename(
                title="Сохранить состав газа как",
                defaultextension=".csv",  # Расширение по умолчанию
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("All files", "*.*"),
                ],  # Фильтр типов файлов
            )

            if not file_path:  # Если пользователь отменил выбор
                self.logger.warning("Отмена.Сохранение отменено пользователем")
                showwarning("Отмена", "Сохранение отменено пользователем")
                return

            # Сохраняем данные в выбранный файл
            with open(file_path, mode="w", newline="", encoding="utf-8") as csvfile:
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

    def load_gas_composition_from_csv(self) -> Dict[str, float]:
        """Loads the gas composition from a CSV file"""
        try:
            # Открываем проводник для выбора файла
            file_path = filedialog.askopenfilename(
                title="Выберите файл для загрузки состава газа",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("All files", "*.*"),
                ],  # Фильтр типов файлов
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
            with open(file_path, mode="r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)
                loaded_composition = {}
                for row in reader:
                    try:
                        loaded_composition[row["Component"]] = float(row["Percentage"])
                    except ValueError:
                        loaded_composition[row["Component"]] = (
                            0.0  # Если значение некорректно, записываем 0.0
                        )
                        self.logger.warning(
                            f"{loaded_composition[row['Component']]} = 0.0"
                        )

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
    """Работа с базой данных SQL_Lite"""

    def __init__(self):
        self.logger = logging.getLogger("App.DataBaseManager")  # Дочерний логгер
        self.db_path = "tables.db"  # Путь к файлу базы данных SQLite
        if os.path.exists("tables.db"):
            os.remove("tables.db")
        self._create_initial_data_table()
    
    def _create_initial_data_table(self):
            """Создает таблицу Initial_Data если она не существует"""
            create_query = """
                CREATE TABLE IF NOT EXISTS "Initial_Data" (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    table_name TEXT NOT NULL,
                    table_type TEXT NOT NULL,
                    parameters TEXT NOT NULL
                )
            """
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(create_query)
        
    def _check_exist_table(self,table_name:str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT 1 FROM "Initial_Data" WHERE table_name = ? LIMIT 1', 
                (table_name,)
            )
            return cursor.fetchone() is not None

    def _create_table_query(self, table_name: str,colums: List[str]) -> str:
        """Create a request to create a table in the database"""
        # Проверяем, что колонки не пустые
        if not colums:
            self.logger.error("Список колонок пуст!")
            raise ValueError("Колонки не определены")
        # Формируем SQL-запрос для создания таблицы
        
        create_table_query = f"""
            CREATE TABLE IF NOT EXISTS '{table_name}' (
                {", ".join([f"{col} REAL" for col in colums])}
            )
        """
        self.logger.debug(f"SQL-запрос создания таблицы: {create_table_query} _create_table_query")
        return create_table_query

    def _insert_query(self,table_name: str, colums: List[str]) -> str:
        """Create a request to insert data into the table"""
        insert_query = f"""
            INSERT INTO '{table_name}' ({", ".join(colums)}) 
            VALUES ({", ".join(["?"] * len(colums))})
        """
        self.logger.debug(f"SQL-запрос вставки данных: {insert_query}")
        return insert_query

    def save_data(
        self, data: Dict[str, List[float]], table_name: str, columns: List[str]
    ):
        """Сохраняет данные из Treeview в базу данных."""
        self.logger.info(f"Начинаем сохранение данных таблицы '{table_name}'")
        try:
            self.logger.debug(f"Данные для сохранения: {data}")
            print(data[table_name])
        
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM '{table_name}'")
                cursor.execute(
                    f"INSERT INTO '{table_name}' VALUES ({', '.join(['?'] * len(columns))})",
                    data[table_name],
                )
            self.logger.info(f"Данные таблицы '{table_name}' успешно сохранены")
            showinfo("Успех", "Данные успешно сохранены")

        except sqlite3.OperationalError as e:
            self.logger.error(f"Ошибка сохранения таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить таблицу: {e}")

        except Exception as e:
            self.logger.exception(
                f"Неожиданная ошибка при сохранении таблицы '{table_name}'"
            )
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def load_data(self, table_name: str) -> Dict[str, float]:
        """Загружает данные таблицы в Treeview."""
        self.logger.info(f"Начинаем загрузку данных таблицы '{table_name}'")

        try:
            if self._check_exist_table(table_name):
                with sqlite3.connect(self.db_path) as conn:
                    df = pd.read_sql_query(f"SELECT parameters FROM 'Initial_Data' WHERE table_name = '{table_name}'", conn)
                    self.logger.debug(f"Загружены данные: \n{df.to_string()}")

                    parameters_json = df['parameters'].loc[0]  # '{"kv": 50, "lines_count": 1}'

                    # Преобразуем JSON-строку в словарь
                    row_dict = json.loads(parameters_json)

                    print(f"{type(row_dict)=}")
                self.logger.info(f"Данные таблицы '{table_name}' успешно загружены")
                return row_dict
            else:
                self.logger.info(f"Таблицы '{table_name}' не существует инициализируем пустой")
                return None

        except sqlite3.OperationalError as e:
            self.logger.error(f"Ошибка загрузки таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить таблицу: {e}")
            return []

        except Exception as e:
            self.logger.exception(
                f"Неожиданная ошибка при загрузке таблицы '{table_name}'"
            )
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
            return []

    def create_table(self, table_name : str, parametr_table : Dict[str,float]):
        """Create table in databaze"""
        # Логирование начала создания таблицы
        self.logger.info(f"Начинаем создание таблицы '{table_name}'")
        columns = list(parametr_table)
        data = list(parametr_table.values())
        try:
            # Проверяем, что колонки не пустые
            if not columns:
                self.logger.error("Список колонок пуст!")
                raise ValueError("Колонки не определены")

            # Формируем SQL-запрос для создания таблицы
            create_table_query = self._create_table_query(columns, table_name)
            self.logger.debug(f"SQL-запрос создания таблицы: {create_table_query}")

            # Формируем SQL-запрос для вставки данных
            insert_query = self._insert_query(table_name, columns)
            self.logger.debug(f"SQL-запрос вставки данных: {insert_query}")

            # Подключаемся к базе данных
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Выполняем создание таблицы
                self.logger.info(
                    f"Выполняем создание таблицы '{table_name}' в базе данных"
                )

                cursor.execute(create_table_query)
                self.logger.debug("Таблица успешно создана или уже существует")

                # Выполняем вставку пустых данных для инициализации
                self.logger.info(
                    "Выполняем вставку пустых данных для инициализации таблицы"
                )
                cursor.execute(insert_query, data)
                self.logger.debug("Данные успешно вставлены")

        except sqlite3.OperationalError as e:
            self.logger.error(f"Ошибка SQLite при создании таблицы '{table_name}': {e}")
            self.logger.error(f"Запрос: {create_table_query}")
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {e}")
        except Exception as e:
            self.logger.exception(
                f"Неожиданная ошибка при создании таблицы '{table_name}'"
            )
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            self.logger.info(
                f"Таблица '{table_name}' успешно создана и инициализирована"
            )

    def add_initial_table(self,table_name : str,table_type:str, parametr_table : Dict[str,float]):
        self.logger.info(f"Начинаем создание таблицы '{table_name}'")
        
        try:
            if not parametr_table:
                self.logger.error("Список параметров пуст!")
                raise ValueError("Параметры не определены")

            # Создаем JSON из параметров для хранения в одной колонке
            import json
            parameters_json = json.dumps(parametr_table, ensure_ascii=False)
            
            # Подготавливаем данные
            data = [table_name, table_type, parameters_json]
            columns = ["table_name", "table_type", "parameters"]  # Фиксированные названия колонок

            # Вставляем данные
            insert_query = self._insert_query("Initial_Data", columns)
            self.logger.debug(f"SQL-запрос вставки данных: {insert_query}")

            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(insert_query, data)
                conn.commit()
                
            self.logger.info(f"Таблица '{table_name}' успешно создана и инициализирована")

        except Exception as e:
            self.logger.exception(f"Ошибка при создании таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {e}")

    def get_data_table(self, name_table) -> List[Dict[str, Any]]:  # убрать оттуда
        """Получение данных из базы данных."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {name_table}", conn)
            self.logger.info(f"Данные таблицы {name_table} полученны из баззы данных")
        return df.to_dict(orient="records")[0]  # Список словарей
    
    def save(self,df,name_P_out):
        print(f"{name_P_out=}")
        column = df.columns.tolist()
        print(f"{df.index.tolist()=}")
        # Формируем SQL-определение столбцов
        column_definitions = ", ".join([f"{col} REAL" for col in column])
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # cursor.execute(f"DELETE FROM {name_P_out}")  # Очистка таблицы
            print(f"{df.iloc[0]=}")
            create_table_query = f"CREATE TABLE IF NOT EXISTS \"{name_P_out}\" (table_name TEXT,{column_definitions})"
            print(f"{create_table_query=}")
            cursor.execute(create_table_query)
            # Добавляем данные из DataFrame
            df.to_sql(name_P_out, conn, if_exists="replace", index=True,index_label =  "table_name")
        self.logger.info(f"Промежуточная таблица {name_P_out=} сохранена в базе данных")

class JsonManager:
    """Работа с файлами типа Json"""

    def __init__(self):
        self.logger = logging.getLogger("App.JsonManager")  # Дочерний логгер
        self.saves_dir = "Saves"

    def save_configure(self, data):
        
        os.makedirs(self.saves_dir, exist_ok=True)  # Создаем директорию, если её нет

        file_path = filedialog.asksaveasfilename(
            title="Сохранить файл",
            initialdir=self.saves_dir,
            defaultextension=".json",  # Расширение по умолчанию
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],  # Фильтр типов файлов
        )
        with open(file_path, "w", encoding="utf-8") as outfile:
            json.dump(data, outfile, indent=4, ensure_ascii=False)

    def load_data(self):
        file_path = filedialog.askopenfilename(
            title="Выберите файл для загрузки состава газа",
            defaultextension=".json",  # Расширение по умолчанию
            filetypes=[
                ("JSON files", "*.json"),
                ("All files", "*.*"),
            ],  # Фильтр типов файлов
        )
        with open(file_path, "r", encoding="utf-8") as outfile:
            data = json.load(outfile)

        return data

class DataStorage:
    """Хранилище данных для работы с данными в программе"""

    def __init__(self):
        self.logger = logging.getLogger("App.DataStorage")  # Дочерний логгер
        self.gas_composition = {}
        self.input_pressure_range = []
        self.output_pressure_range = None
        self.tables_data = {}
        self.gas_properties = {}
        self._temperature = {}
        self.db_path = "tables.db"

    @property
    def data_gas_composition(self) -> Dict[str, float]:
        return self.gas_composition

    @data_gas_composition.setter
    def data_gas_composition(self, composition: Dict[str, float]):
        """Устанавливает состав газа. Ожидается уже провалидированный словарь."""
        if not isinstance(composition, dict):
                self.logger.error("Попытка установить состав газа не словарем.")
                raise ValueError("Попытка установить состав газа не словарем.")

        self.gas_composition = composition
       
    def get_input_pressure_range(self) -> List[float]:
        return self.input_pressure_range

    def get_output_pressure_range(self) -> List[float]:
        return self.output_pressure_range

    def set_pressure_range(self, pressure_type: str, pressure_range: List[float]):
        """
        Устанавливает диапазон давлений (входного или выходного).
        :param pressure_type: "input" для входного давления, "output" для выходного.
        """
        try:
            # Если диапазон не сгенерирован (ошибка), прерываем выполнение
            if pressure_range is None:
                self.logger.error(
                    f"Диапазон {pressure_type} давлений не был сгенерирован"
                )
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

    @property
    def table_manager(self) -> Dict[str, Any]:
        """Возвращаем название и тип таблиц"""
        return self.tables_data

    @table_manager.setter
    def table_manager(self, tables: Dict[str, BaseTableManager]):
        self.tables_data.update(tables)
        print(self.tables_data)
        # for i in self.tables_data:
        #     # print(f"{self.tables_data[i].get_table_type()=}")
        self.logger.info(f"Данные таблицы {self.tables_data} добавлены в Data_model")

    @property
    def temperature(self) -> Dict[str, float]:
        return self._temperature

    @temperature.setter
    def temperature(self, temp: Dict[str, float]):
        self._temperature = temp
        self.logger.info(
            f"Данные температуры газа {self._temperature} сохранены в Data_model"
        )
        showinfo("Успех", "Данные успешно сохранены!")
