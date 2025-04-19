import contextlib
from abc import ABC,abstractmethod
import tkinter as tk
from tkinter import FALSE, Menu, ttk,filedialog
import math
from tkinter import messagebox
from tkinter.messagebox import showwarning, showinfo
import Calculate_file
import numpy as np
import pandas as pd
import os  # Import the 'os' module
import csv
import sqlite3
from typing import List, Dict, Any,Optional,TypedDict
import logger_config
import matplotlib.pyplot as plt
import json
from wigets  import WidgetFactory
from DataModel import Data_model

class WidgetFactory:  
    @staticmethod
    def create_entry(parent, row,column=1, padx=5, pady=5):
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=column, padx=padx, pady=pady)
        return entry
    
    @staticmethod
    def create_label(parent, label_text, row, column=0, padx=5, pady=5):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky="w")
        return label
    
    @staticmethod
    def create_Button(parent, label_text, row, function=None, column=0, padx=5, pady=5):
        Button = ttk.Button(parent, text=label_text, command=function)
        Button.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
        return Button

class GuiManager:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.style = ttk.Style(root)
        self._create_menu()
        self._create_style()
        self.tabs = {}
        self._create_notebook()
        # Создаем словарь для хранения фреймов
        

        self.root.title("Расчеты газовых систем")
        self.root.geometry("700x300")  # Начальный размер окна
        self.root.minsize(700, 300)     # Минимальный размер окна
        
        # Инициализация менеджеров для каждой функциональности
        
        self.gas_composition_manager = Initial_data(self.tabs["Исходные данные"])
        self.gas_properties_manager = Calculation_gas_properties(self.tabs)
        self.tube_properties_manager = Calculation_pipi(self.tabs)
        self.regulatormanager = Calculation_regulator(self.tabs)
        self.heatbalancemanager = Heat_balance(self.tabs)

    def _create_menu(self):
        self.root.option_add("*tearOff", FALSE)

        main_menu = Menu()

        file_menu = Menu()
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")

        main_menu.add_cascade(label="Файл",menu=file_menu)
        main_menu.add_cascade(label="Настройка")
        main_menu.add_cascade(label="Справка")
        self.root.config(menu=main_menu)

    def _create_style(self): 
        # Настраиваем стили
        # Убираем пунктирную рамку вокруг активной вкладки
        # Полностью убираем рамки и выделение для вкладок
        self.style.configure("TNotebook.Tab",
            background="#e0e0e0",      # Цвет фона вкладки
            padding=[10, 5],           # Отступы внутри вкладки
            font=("Arial", 10, "bold"),
            borderwidth=0,             # Нет границ
            highlightthickness=0       # Нет выделения
        )

        # Для активной вкладки (убираем рамку при выборе)
        self.style.map("TNotebook.Tab",
            background=[("selected", "#d0d0d0")],
            expand=[("selected", [0, 0, 0, 0])]  # Убираем расширение рамки
        )
        self.style.theme_use("clam")  # Современная тема
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure("TButton", font=("Arial", 10, "bold"), padding=5, background="#4CAF50")
        self.style.configure("Treeview", rowheight=25, font=("Arial", 10))

    def _create_notebook(self):   
        # Создаем Notebook с стилем
        self.notebook = ttk.Notebook(root, style="Custom.TNotebook")
        self.style.configure("Custom.TNotebook", tabposition="n", background="#e0e0e0")
        self.notebook.pack(fill="both", expand=True)

        # Создаем ссписок для названий вкладок расчетов
        tabs_name = ["Исходные данные", "Свойства газа", "Расчет пропускной способности трубы", "Расчет регулятора", "Тепловой баланс"]
        
        for name in tabs_name:
            frame = ttk.Frame(self.notebook)
            self.tabs[name] = frame  # Сохраняем фрейм в словаре
            self.notebook.add(frame, text=name)

class Initial_data:
    def __init__(self,parent):
        self.parent = parent
        # self.data_model=data_model
        self.create_wigets()
        self.entries = {} #Словарь хранения данных
        self.callbacks = {}  # Хранилище для колбэков
    
    def create_wigets(self):
        self.gas_button = WidgetFactory.create_Button(self.parent,label_text="Ввести состав газа", row=1,function=lambda: self.callbacks.get("save_gas_composition")()) 
        self.button_temp = WidgetFactory.create_Button(parent=self.parent,label_text="Температура газа",row=2,function=self.create_window_temperature)
        self.input_pressure = WidgetFactory.create_Button(parent=self.parent, label_text="Диапазон входных давлений",row=3,function=lambda: self.callbacks.get("input_pressure")())
        self.output_pressure = WidgetFactory.create_Button(parent=self.parent, label_text="Диапазон выходных давлений",row=4,function=lambda: self.callbacks.get("output_pressure")())
        self.input_table_button = WidgetFactory.create_Button(parent=self.parent,label_text="Исходные таблицы",row=5,function=self.create_window_table)
        self.calculate_button = WidgetFactory.create_Button(self.parent, label_text="Автоматический расчет",row=6)
        self.calculate_button.config(state="disabled")
 
    def create_window_sostav_gaz(self):
        # Окно для ввода состава газа
        self.gas_window = tk.Toplevel(self.parent)
        self.gas_window.title("Состав газа")

        # Список компонентов с формулами
        self.components = [
            "Метан: CH4", "Этан: C2H6", "Пропан: C3H8", "н-Бутан: n-C4H10", "и-Бутан: i-C4H10",
            "н-Пентан: n-C5H12", "и-Пентан: i-C5H12", "н-Гексан: n-C6H14", "н-Гептан: n-C7H16", "н-Октан: n-C8H18",
            "Ацетилен: C2H2", "Этилен: C2H4", "Пропилен: C3H6", "Бензол: C6H6", "Толуол: C7H8",
            "Водород: H2", "Водяной пар: H2O", "Аммиак: NH3", "Метанол: CH3OH", "Сероводород: H2S",
            "Метилмеркаптан: CH3SH", "Диоксид серы: SO2", "Гелий: He", "Неон: Ne", "Аргон: Ar",
            "Моноксид углерода: CO", "Азот: N2","Воздух", "Кислород: O2", "Диоксид углерода: CO2"
        ]
        # Создаем метки и поля ввода для каждого компонента
        
        mediana = int((len(self.components)/2.0)) - 1
        for i, component in enumerate(self.components):

            if i <=mediana:
                label = WidgetFactory.create_label(self.gas_window, component,i,0)
                enty = WidgetFactory.create_entry(self.gas_window,i,1)
            else:
                label = WidgetFactory.create_label(self.gas_window, component,i-15,3)
                enty = WidgetFactory.create_entry(self.gas_window,i-15,4)
            enty.bind("<KeyRelease>", self.update_total_percentage)
            self.entries[component] = enty

        self.total_label = WidgetFactory.create_label(parent=self.gas_window,label_text="Сумма: 0.0%",row=math.floor((len(self.components)/2)),column = 4  )
        # Load previously saved composition, if available

        self.row_last_components = math.ceil((len(self.components)/2)+1)

        # Кнопка для сохранения данных
        self.save_gaz_sostav_button = WidgetFactory.create_Button(self.gas_window, "Сохранить", 
                                                                  self.row_last_components,function=lambda: self.callbacks.get("save_sostav_gaz")())
        #Кнопка для сохранения в файл
        self.save_to_file_button = WidgetFactory.create_Button(parent=self.gas_window,label_text="Сохранить в файл",
                                                               row = self.row_last_components+1,function=lambda: self.callbacks.get("save_gas_composition_to_csv")())
         #Кнопка для открытия из файла
        self.load_from_file_button = WidgetFactory.create_Button(self.gas_window,"Открыть из файла",
                                                                 self.row_last_components+2,function=lambda: self.callbacks.get("load_gas_composition_to_csv")())

    def update_total_percentage(self, event=None):
        """
        Подсчитывает сумму процентов из всех полей ввода и обновляет метку.
        """
        total = 0.0
        for component, entry in self.entries.items():
            with contextlib.suppress(ValueError):
                value = float(entry.get())
                total += value
        # Обновляем метку с суммой
        self.total_label.config(text=f"Сумма: {total:.4f}%")

    def create_window_temperature(self):
        """Открывает диалог для ввода температур."""
        self.entries_dict = {}
        pressure_window = tk.Toplevel(self.parent)
        pressure_window.attributes('-topmost', True)
        pressure_window.title("Температурный режим")

        for idx, (title, label_text) in enumerate([
            ("input", "Температура на входе"),
            ("output", "Температура на выходе")
        ]):
            WidgetFactory.create_label(parent=pressure_window, label_text=label_text, row=idx)
            entry = WidgetFactory.create_entry(parent=pressure_window, row=idx)
            self.entries_dict[title] = entry  # Сохраняем Entry по имени

        print(self.entries_dict)
        
        # # temperature = self.data_model.get_temperature()
        # print(f"{temperature=}")
        # if temperature:
        #     # min_pressure_entry.insert(0, min(pressure_range))

        #     self.entries_dict["input"].insert(0,temperature['in'])
        #     self.entries_dict["output"].insert(0,temperature['out'])
            
        self.save_button = WidgetFactory.create_Button(
            pressure_window,
            label_text="Сохранить",
            row=3)

    def create_window_pressure(self,title):
        """
        Открывает диалоговое окно для ввода диапазона давлений.
        """
        self.title =title
        pressure_window = tk.Toplevel(self.parent)
        pressure_window.title(self.title)

        labels = ["Минимальное давление:", "Максимальное давление:", "Шаг значения"]
        self.pressure_entries = {}

        for i, label_text in enumerate(labels):
            ttk.Label(pressure_window, text=label_text).grid(row=i, column=0, padx=5, pady=5)
            entry = WidgetFactory.create_entry(pressure_window, row=i, column=1)
            self.pressure_entries[labels[i]] = entry
        print(self.pressure_entries)  

        self.save_button = WidgetFactory.create_Button(parent=pressure_window,label_text="Сохранить",row=4,function=lambda: self.callbacks.get("save_pressure_range")())
   
    def create_window_table(self):
        self.tables = {}  # Хранит все таблицы: {"table_name": manager}
        self.table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной",
            "Таблицы для труб до регулятора",
            "Таблицы для труб после регулятора"
        ]
        self.table_window = tk.Toplevel(self.parent)
        self.table_window.title("Таблицы граничных условий")

        # Метка для выбора таблицы
        label = WidgetFactory.create_label(self.table_window, "Выберите таблицу:", 0)

        # Combobox
        self.combobox = ttk.Combobox(
            self.table_window,
            values=self.table_labels,
            state="readonly",
            width=33
        )
        self.combobox.grid(row=1, column=0, padx=5, pady=5)

        # Кнопка добавления таблицы
        save_button = WidgetFactory.create_Button(
            self.table_window,
            "Добавить таблицу",
            2,
        )

    def register_callback(self, event_name, callback):
        """
        Регистрирует колбэк для определённого события.
        """
        self.callbacks[event_name] = callback

class Сontroller:
    def __init__(self,initial_data:Initial_data,model:'Model'):
        self.initial_data = initial_data
        self.model = model

        #Регистрируем колбеки
        self.initial_data.register_callback("save_gas_composition", self.gaz_window)# "Сохранить состав газа"
        for pressure_type in ["input", "output"]:
            self.initial_data.register_callback(
                f"{pressure_type}_pressure",
                lambda pt=pressure_type: self.setup_button_pressure(pt)
            )# Колбек на открытия меню входного и выходного давления
        self.initial_data.register_callback("save_gas_composition_to_csv",self.save_sostav_csv)
        self.initial_data.register_callback("load_gas_composition_to_csv",self.model.load_gaz_from_csv)
        self.initial_data.register_callback("save_sostav_gaz",lambda : self.model.save_sostav_gaz(self.initial_data.entries))
        
    def setup_button_pressure(self,title): # Функция для создание диапазона входных и выходных давлений
        self.initial_data.create_window_pressure(title) #Создаем окно
        # # Загрузка предыдущих значений
        if pressure_range := getattr(self.model.data_model, f"get_{title.lower()}_pressure_range")():
            self.initial_data.pressure_entries["Минимальное давление:"].insert(0, min(pressure_range))
            self.initial_data.pressure_entries["Максимальное давление:"].insert(0, max(pressure_range))
            self.initial_data.pressure_entries["Шаг значения"].insert(0, pressure_range[1] - pressure_range[0])

        self.initial_data.register_callback("save_pressure_range", lambda: self.model.save_pressure_range1(   
                self.initial_data.title,  # Передаем title
                self.initial_data.pressure_entries  # Передаем поля для ввода
            ))# Привязываю функцию для сохранение диапазона давлениея
        
    def gaz_window(self):
        self.initial_data.create_window_sostav_gaz()
        self.model.load_gas_composition(self.initial_data.entries)
        self.initial_data.update_total_percentage()
    
    def save_sostav_csv(self):
        self.model.save_sostav_gaz(self.initial_data.entries)
        self.model.save_gaz_from_csv()

class Model:
    def __init__(self, data_model: Data_model):
        self.data_model = data_model

    def _calculate_pressure_range(self, min_pressure, max_pressure, average_value) -> List[float]:
        try:

            # Проверка корректности данных
            if min_pressure > max_pressure:
                raise ValueError("Ошибка: Минимальное давление больше максимального.")
            if average_value <= 0:
                raise ValueError("Ошибка: Шаг должен быть положительным числом.")

            pressure_range = np.arange(min_pressure, max_pressure + average_value, average_value).tolist()
            return [round(p, 1) for p in pressure_range]
        
        except ValueError as e:
            # Вывод ошибки
            showwarning("Ошибка", e)
            return 
    
    def save_pressure_range1(self, title: str, pressure_entries: Dict[str,ttk.Entry]):
        """
        Сохраняет диапазон давлений.
        """
        # Преобразуем входные данные в числа
        min_pressure = float(pressure_entries["Минимальное давление:"].get())
        max_pressure= float(pressure_entries["Максимальное давление:"].get())
        avg_value= float(pressure_entries["Шаг значения"].get())
        
        if not all([min_pressure, max_pressure, avg_value]):
                        raise ValueError("Ошибка: Введите значения")

        try:
            pressure_type = title.lower()
            set_pressure_range=self._calculate_pressure_range(min_pressure, max_pressure, avg_value)

            print(f"{set_pressure_range=}")
            self.data_model.set_pressure_range(pressure_type,set_pressure_range)

            logger.info(f"Диапазоны {pressure_type} давления  успешно сохранены: максимальное = %s мПа, минимальное = %s мПа,шаг = %s", max_pressure, min_pressure,avg_value)
        except ValueError:
            logger.warning("Введите корректные числовые значения!")
            showwarning("Ошибка", "Введите корректные числовые значения!")

    def load_gas_composition(self,entries):
        """Loads the gas composition from the data model and updates the entry fields."""
        saved_composition = self.data_model.data_gas_composition
        for component, entry in entries.items():
            if component in saved_composition:
                entry.delete(0, tk.END)
                entry.insert(0, str(saved_composition[component]))

    def save_sostav_gaz(self,entries):
        self.data_model.data_gas_composition = entries   

    def save_gaz_from_csv(self):

        self.data_model.save_gas_composition_to_csv()
    
    def load_gaz_from_csv(self):
        self.data_model.load_gas_composition_from_csv()


class BaseTableManager(ABC):
    def __init__(self,parent,table_type):
        self.parent = parent
        self.db_path = "tables.db"  # Путь к файлу базы данных SQLite
        self.table_type = table_type

    @abstractmethod
    def get_columns(self) -> list:
        pass
    
    def get_table_type(self) -> str:
        return self.table_type
    
    def create_table(self,table_name):#Перенести в model
        """Create table in databaze"""
            # Логирование начала создания таблицы
        logger.info(f"Начинаем создание таблицы '{table_name}'")
        try:
            # Получаем список колонок из подкласса
            columns = self.get_columns()
            logger.debug(f"Получены колонки: {columns}")

            # Проверяем, что колонки не пустые
            if not columns:
                logger.error("Список колонок пуст!")
                raise ValueError("Колонки не определены")

            # Формируем SQL-запрос для создания таблицы
            create_table_query = f'''
                CREATE TABLE IF NOT EXISTS '{table_name}' (
                    {", ".join([f"{col} REAL" for col in columns])}
                )
            '''
            logger.debug(f"SQL-запрос создания таблицы: {create_table_query}")

            # Формируем SQL-запрос для вставки данных
            insert_query = f'''
                INSERT INTO '{table_name}' ({", ".join(columns)}) 
                VALUES ({", ".join(["?"] * len(columns))})
            '''
            logger.debug(f"SQL-запрос вставки данных: {insert_query}")

            # Подключаемся к базе данных
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Выполняем создание таблицы
                logger.info(f"Выполняем создание таблицы '{table_name}' в базе данных")
                cursor.execute(create_table_query)
                logger.debug("Таблица успешно создана или уже существует")

                # Выполняем вставку пустых данных для инициализации
                logger.info("Выполняем вставку пустых данных для инициализации таблицы")
                cursor.execute(insert_query, [""] * len(columns))
                logger.debug("Данные успешно вставлены")

        except sqlite3.OperationalError as e:
            logger.error(f"Ошибка SQLite при создании таблицы '{table_name}': {e}")
            logger.error(f"Запрос: {create_table_query}")
            messagebox.showerror("Ошибка", f"Не удалось создать таблицу: {e}")
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при создании таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
        else:
            logger.info(f"Таблица '{table_name}' успешно создана и инициализирована")
        
    def load_table(self, table_name): #Перенести в data_model
        """Загружает данные таблицы в Treeview."""
        logger.info(f"Начинаем загрузку данных таблицы '{table_name}'")
        try:
            with sqlite3.connect(self.db_path) as conn:
                df = pd.read_sql_query(f"SELECT * FROM '{table_name}'", conn)
                logger.debug(f"Загружены данные: \n{df.to_string()}")
                for _, row in df.iterrows():
                    self.tree.insert("", "end", values=list(row))
            logger.info(f"Данные таблицы '{table_name}' успешно загружены")
        except sqlite3.OperationalError as e:
            logger.error(f"Ошибка загрузки таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить таблицу: {e}")
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при загрузке таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")

    def save_data(self, tree, table_name,window): #Перенести в data_model
        """Сохраняет данные из Treeview в базу данных."""
        logger.info(f"Начинаем сохранение данных таблицы '{table_name}'")
        try:
            data = [tree.item(item)["values"] for item in tree.get_children()]
            logger.debug(f"Данные для сохранения: {data}")
            columns = self.get_columns()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM '{table_name}'")
                cursor.executemany(f"INSERT INTO '{table_name}' VALUES ({', '.join(['?']*len(columns))})", data)
            logger.info(f"Данные таблицы '{table_name}' успешно сохранены")
            showinfo("Успех","Данные успешно сохранены")
            window.destroy()
        except sqlite3.OperationalError as e:
            logger.error(f"Ошибка сохранения таблицы '{table_name}': {e}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить таблицу: {e}")
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при сохранении таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Произошла непредвиденная ошибка: {e}")
    
    def add_editing_features(self,event):
        """Обработка двойного клика для редактирования ячейки."""
        # Получаем выбранную строку и столбец
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return

        # Получаем ID строки и имя столбца
        item_id = self.tree.focus()
        column = self.tree.identify_column(event.x)
        column_index = int(column[1:]) - 1  # Индекс столбца (начиная с 0)

        # Значение текущей ячейки
        current_value = self.tree.item(item_id)["values"][column_index]

        # Создаем Entry для редактирования
        entry = ttk.Entry(self.tree)
        entry.insert(0, str(current_value))
        entry.focus()

        # Размещение Entry поверх ячейки
        x, y, width, height = self.tree.bbox(item_id, column)
        entry.place(x=x, y=y, width=width, height=height)

        # Обработка завершения редактирования
        def save_edit(event=None):
            new_value = entry.get()
            values = list(self.tree.item(item_id)["values"])
            values[column_index] = new_value
            self.tree.item(item_id, values=values)
            entry.destroy()
        entry.bind("<Return>", save_edit)  # Сохранение при нажатии Enter
        entry.bind("<FocusOut>", save_edit)  # Сохранение при потере фокуса

    def open_table_window(self, table_name):# Перенести в Gui
        """Открывает окно с таблицей."""
        logger.info(f"Открытие окна таблицы '{table_name}'")
        try:
            window = tk.Toplevel(self.parent)
            window.title(f"Таблица: {table_name}")
            logger.debug(f"Создано новое окно для таблицы '{table_name}'")

            self.tree = ttk.Treeview(window, columns=self.get_columns(), show="headings")
            for col in self.get_columns():
                self.tree.heading(col, text=col)
            self.tree.pack(fill="both", expand=True)
            logger.debug("Treeview инициализирован с колонками")

            self.load_table(table_name)
            logger.debug("Данные загружены в Treeview")

            save_button = ttk.Button(
                window,
                text="Сохранить данные",
                command=lambda: self.save_data(self.tree, table_name,window)
            )
            save_button.pack(pady=10)
            logger.debug("Кнопка сохранения добавлена в окно")

            self.tree.bind("<Double-1>", self.add_editing_features)
            logger.debug("Событие двойного клика привязано к редактированию ячеек")

        except Exception as e:
            logger.exception(f"Ошибка при открытии окна таблицы '{table_name}'")
            messagebox.showerror("Ошибка", f"Не удалось открыть таблицу: {e}")

class RegulatorTableManager(BaseTableManager):
    
    def get_columns(self):
        return ["regulator", "kv", "lines_count"]

class BoilerTableManager(BaseTableManager):
    def get_columns(self):
        return ["boiler_power", "gas_temp_in", "gas_temp_out"]

class PipeTableManager(BaseTableManager):
    def get_columns(self):
        return ["pipe_diameter", "wall_thickness", "gas_speed", "gas_temperature", "lines_count"]

class TableFactory:
    @staticmethod
    def create_table_manager(table_type, parent):
        logger.info(f"Запрос на создание менеджера таблицы типа: '{table_type}'")
        logger.debug(f"Параметры: parent={parent}")

        match table_type:
            case "Таблица для регуляторов":
                logger.info("Создан менеджер таблицы регуляторов")
                return RegulatorTableManager(parent,table_type)
            
            case "Таблица котельной":
                logger.info("Создан менеджер таблицы котельной")
                return BoilerTableManager(parent,table_type)
            
            case "Таблицы для труб до регулятора" | "Таблицы для труб после регулятора":
                logger.info(f"Создан менеджер таблицы труб: {table_type}")
                return PipeTableManager(parent,table_type)
            
            case _:
                error_msg = f"Неизвестный тип таблицы: {table_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)

class TableManager:
    def __init__(self, parent, data_model):
        logger.info("Инициализация TableManager")
        self.parent = parent
        self.data_model = data_model
        self.tables = {}  # Хранит все таблицы: {"table_name": manager}
        logger.debug("Создание виджетов для управления таблицами")
        self.create_widgets()
        self.table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной",
            "Таблицы для труб до регулятора",
            "Таблицы для труб после регулятора"
        ]
        logger.debug(f"Список доступных типов таблиц: {self.table_labels}")
        self.row = 4

    def create_widgets(self):
        logger.info("Создание кнопки 'Исходные таблицы'")
        input_table_button = ttk.Button(
            self.parent,
            text="Исходные таблицы",
            command=self.check_table_func
        )
        input_table_button.grid(row=5, column=0, padx=10, pady=5, sticky="ew")
        logger.debug("Кнопка 'Исходные таблицы' размещена в интерфейсе")

    def create_window_table(self):
        logger.info("Создание окна выбора таблиц")
        self.table_window = tk.Toplevel(self.parent)
        self.table_window.title("Таблицы граничных условий")
        logger.debug("Окно таблиц создано")
        
        # Метка для выбора таблицы
        label = WidgetFactory.create_label(self.table_window, "Выберите таблицу:", 0)
        logger.debug("Метка 'Выберите таблицу' добавлена в окно")

        # Combobox
        self.combobox = ttk.Combobox(
            self.table_window,
            values=self.table_labels,
            state="readonly",
            width=33
        )
        self.combobox.grid(row=1, column=0, padx=5, pady=5)
        logger.debug(f"Combobox инициализирован с вариантами: {self.table_labels}")

        # Кнопка добавления таблицы
        save_button = WidgetFactory.create_Button(
            self.table_window,
            "Добавить таблицу",
            2,
            self.define_table
        )
        logger.debug("Кнопка 'Добавить таблицу' добавлена в окно")

    def check_table_func(self):
        logger.info("Вызов метода check_table_func")
        if len(self.tables) == 0:
            logger.warning("Список таблиц пуст. Создаем новое окно.")
            self.create_window_table()
        else:
            logger.info("Список таблиц не пуст. Обновляем окно.")
            self.create_window_table()
            for name in self.tables:
                logger.debug(f"Добавление метки для таблицы: {name}")
                print(f"{self.tables=}")
                label = WidgetFactory.create_label(
                    self.table_window,
                    self.tables[name].get_table_type(),
                    self.row
                )
                entry = WidgetFactory.create_entry(self.table_window, self.row, 1)
                entry.insert(0, name)
                open_button = WidgetFactory.create_Button(
                    parent =self.table_window,
                    label_text="Открыть таблицу",
                    row=self.row,
                    function=lambda tn=name, tt=self.tables[name].get_table_type(): self.open_table(tn, tt),
                    column=3
                )
                self.row += 1
                logger.debug(f"Метка и кнопка для таблицы '{name}' добавлены в окно")

    def define_table(self):
        logger.info("Начало определения новой таблицы")
        selection = self.combobox.get()
        if not selection:
            logger.error("Тип таблицы не выбран")
            print("Ошибка: Таблица не выбрана!")
            return
        logger.debug(f"Выбранный тип таблицы: {selection}")
        self.row += 1

        # Метка с названием таблицы
        logger.debug("Создание метки для нового типа таблицы")
        label = WidgetFactory.create_label(
            self.table_window,
            label_text=selection,
            row=self.row
        )

        # Поле ввода имени таблицы
        logger.debug("Создание поля ввода имени таблицы")
        entry = WidgetFactory.create_entry(self.table_window, self.row, 1)

        # Кнопка для открытия таблицы
        open_button = WidgetFactory.create_Button(
            self.table_window,
            "Открыть таблицу",
            self.row,
            lambda: self.open_table(entry.get(), selection),
            3
        )
        logger.info("Интерфейс для создания/открытия таблицы инициализирован")

    def add_table(self, table_name, table_type):
        logger.info(f"Попытка добавления таблицы '{table_name}' типа '{table_type}'")
        
        if table_name  == "":
            messagebox.showwarning("Ошибка", "Введите название таблицы")
            return

        if table_name in self.tables:
            logger.warning(f"Таблица '{table_name}' уже существует")
            messagebox.showwarning("Ошибка", f"Таблица '{table_name}' уже существует!")
            return
        
        logger.debug("Создание менеджера таблицы через TableFactory")
        manager = TableFactory.create_table_manager(table_type, self.parent)
        manager.create_table(table_name)
        print(f"{manager=}")
        self.tables[table_name] = manager
        self.data_model.set_tables_data(self.tables)
        logger.info(f"Таблица '{table_name}' добавлена в реестр")

    def open_table(self, table_name, table_type):
        logger.info(f"Попытка открытия таблицы '{table_name}' типа '{table_type}'")
        if table_name not in self.tables:
            logger.warning(f"Таблица '{table_name}' не найдена. Создаем новую.")
            self.add_table(table_name, table_type)
  
        logger.debug("Открытие окна таблицы через менеджер")
        self.tables[table_name].open_table_window(table_name)
        logger.info(f"Таблица '{table_name}' открыта")































class Calculation_gas_properties:
    def __init__(self, parent):
        self.parent = parent["Свойства газа"]
        # self.data_model = data_model
        self.create_widgets()
        self.list = []

    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(parent=self.parent, label_text="Расчитать",row=2)

        label_pressure = WidgetFactory.create_label(self.parent, "Давление, МПа",0, 0)
        label_temperature = WidgetFactory.create_label(self.parent, "Температура, ℃",1, 0)
        self.entry_pressure = WidgetFactory.create_entry(self.parent,0, 1)
        self.entry_temperature = WidgetFactory.create_entry(self.parent,1, 1)

        self.gaz_text = tk.Text(self.parent, height=10, width=70, state="disabled")
        self.gaz_text.grid(row=0, column=3, rowspan=4, padx=10, pady=5, sticky="nsew")


    def start(self):
        try:
            p_in = float(self.entry_pressure.get())  # Получаем давление
            t_in = float(self.entry_temperature.get())  # Получаем температуру
        except ValueError:
            self.gaz_text.config(state="normal")
            self.gaz_text.delete("1.0", tk.END)
            self.gaz_text.insert(tk.END, "Ошибка: Введите числовые значения для давления и температуры.")
            self.gaz_text.config(state="disabled")
            return

        # gas_composition = self.data_model.data_gas_composition  # Получаем состав газа
        # rho_rab, z, plotnost,Di,Ccp = Calculate_file.data_frame(p_in, t_in, gas_composition)

        # self.data_model.set_gas_properties([rho_rab, z, plotnost,Di,Ccp])

        self.gaz_text.config(state="normal")
        self.gaz_text.delete("1.0", tk.END)
        self.gaz_text.insert(tk.END, f"=== Введенные данные ===\nДавление: {p_in}\nТемпература: {t_in}\n")
        self.gaz_text.insert(tk.END, f"Плотность смеси при рабочих условиях: {rho_rab:.2f} кг/м3 \n")
        self.gaz_text.insert(tk.END, f"Коэффициент сжимаемости: {z}\n")
        self.gaz_text.insert(tk.END, f"Плотность смеси при стандартных условиях: {plotnost:.4f} кг/м3 ")
        self.gaz_text.config(state="disabled")

class Calculation_regulator:
    def __init__(self, parent):
        self.parent = parent["Расчет регулятора"]
        # self.data_model = data_model
        self.entries = {}
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать",9)
        name_label = ["Давление вход, МПа",
                      "Давление выход, МПа",
                      "Температура, ℃",
                      "Kv",
                      "Количество линий"]
        for i,name in enumerate(name_label):
            label = WidgetFactory.create_label(self.parent, name,i, 0)
            entry = WidgetFactory.create_entry(self.parent, i, 1)
            self.entries[name] = entry

        self.regul_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.regul_text.grid(row=0, column=3, rowspan=4, padx=10, pady=5, sticky="nsew")
    
    def calc_regul(self):
        try:
            input_values = {}
            for name, entry in self.entries.items():
                value = float(entry.get())
                input_values[name] = value
            gas_composition = self.data_model.data_gas_composition  # Получаем состав газа
            rho_rab, z, plotnost,Di,Ccp = Calculate_file.data_frame(input_values["Давление вход, МПа"], input_values["Температура, ℃"], gas_composition)
            q = Calculate_file.calculate_Ky(input_values["Давление вход, МПа"],
                               input_values["Давление выход, МПа"],
                               input_values["Температура, ℃"],
                               plotnost,
                               input_values["Kv"],
                               input_values["Количество линий"])
                               
        

        except ValueError:
             self.regul_text.insert(tk.END, "Ошибка: Введите числовые значения.")

        self.regul_text.config(state="normal")
        self.regul_text.delete("1.0", tk.END)
        self.regul_text.insert(tk.END, f"Входное давление = {input_values["Давление вход, МПа"]}\n")
        self.regul_text.insert(tk.END, f"Выходное давление = {input_values["Давление выход, МПа"]}\n")
        self.regul_text.insert(tk.END, f"Расход = {q}\n")
        self.regul_text.config(state="disabled")

class Heat_balance:
    def __init__(self, parent):
        self.parent = parent["Тепловой баланс"]
        # self.data_model = data_model
        self.entries = {}
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать",9)
        name_label = ["Давление вход, МПа",
                      "Давление выход, МПа",
                      "Температура вход, ℃",
                      "Температура выход, ℃",
                      "Мощность котельной, кВт",
                    ]
        for i,name in enumerate(name_label):
            label = WidgetFactory.create_label(self.parent, name,i, 0)
            entry = WidgetFactory.create_entry(self.parent, i, 1)
            self.entries[name] = entry

        self.heat_balance_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.heat_balance_text.grid(row=0, column=3, rowspan=4, padx=10, pady=5, sticky="nsew")
    def calc_heat_balance(self):
        try:
            input_values = {}
            self.heat_balance_text.config(state="normal")
            self.heat_balance_text.delete("1.0", tk.END)
            for name, entry in self.entries.items():
                value = float(entry.get())
                input_values[name] = value
            gas_composition = self.data_model.data_gas_composition  # Получаем состав газа
            rho_rab_in, z_in, plotnost_in,Di_in,Cc_in = Calculate_file.data_frame(input_values["Давление вход, МПа"], input_values["Температура вход, ℃"], gas_composition)
            # rho_rab_out, z_out, plotnost_out,Di_out,Ccp_out = Calculate_file.data_frame(input_values["Давление выход, МПа"], input_values["Температура выход, ℃"], gas_composition)
            q,T = Calculate_file.heat_balance(input_values["Давление вход, МПа"],
                               input_values["Давление выход, МПа"],
                               input_values["Температура вход, ℃"],
                               input_values["Температура выход, ℃"],
                               input_values["Мощность котельной, кВт"],
                               Di_in,
                               Cc_in)
             
        except ValueError:
             self.heat_balance_text.insert(tk.END, "Ошибка: Введите числовые значения.")

        self.heat_balance_text.insert(tk.END, f"Входное давление = {input_values["Давление вход, МПа"]}\n")
        self.heat_balance_text.insert(tk.END, f"Выходное давление = {input_values["Давление выход, МПа"]}\n")
        self.heat_balance_text.insert(tk.END, f"Расход = {q}\n")
        self.heat_balance_text.insert(tk.END, f"Температура после теплообменника = {T}\n")
        self.heat_balance_text.insert(tk.END, f"Среднее значение коэффициента Джоуля-Томсона {Di_in}\n")
        self.heat_balance_text.config(state="disabled")

class Calculation_pipi:
    def __init__(self, parent):
        self.parent = parent["Расчет пропускной способности трубы"]
        # self.data_model = data_model
        self.entries = {}
        self.create_widgets()
        
    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(
            self.parent, "Расчитать", 0
        )

        # Список меток для полей ввода
        name_label = [
            "Давление, Мпа",
            "Температура, ℃",
            "Диаметр трубы, мм",
            "Толщина стенки трубы, мм",
            "Скорость газа в трубе, м/с",
            "Количество линий"
        ]
        # Создаем метки и поля ввода
        start_row = 1  # Начинаем с первой строки после кнопки
        for i, name in enumerate(name_label):
            label = WidgetFactory.create_label(self.parent, name, start_row + i, 0)
            entry = WidgetFactory.create_entry(self.parent, start_row + i, 1)
            self.entries[name] = entry

        # Текстовое поле для вывода результатов
        self.tube_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.tube_text.grid(row=start_row, column=3, rowspan=len(name_label), padx=10, pady=5, sticky="nsew")

        # Настройка веса столбцов и строк
        self.parent.grid_columnconfigure(3, weight=1)
        for i in range(start_row, start_row + len(name_label)):
            self.parent.grid_rowconfigure(i, weight=1)

    def calc_tube(self):
        try:
            # Получаем входные данные
            input_values = {}
            for name, entry in self.entries.items():
                value = float(entry.get())
                input_values[name] = value

            # Получаем состав газа
            gas_composition = self.data_model.data_gas_composition

            # Выполняем расчеты
            rho_rab, z, plotnost, Di, Ccp = Calculate_file.data_frame(
                input_values["Давление, Мпа"], input_values["Температура, ℃"], gas_composition
            )

            q = Calculate_file.calc(
                input_values["Диаметр трубы, мм"],
                input_values["Толщина стенки трубы, мм"],
                input_values["Давление, Мпа"],
                input_values["Температура, ℃"],
                input_values["Скорость газа в трубе, м/с"],
                input_values["Количество линий"],
                z,
            )

            # Обновляем текстовое поле через отдельный метод
            self.update_tube_text(q, plotnost)

        except ValueError:
            self.update_tube_text(error_message="Ошибка: Введите числовые значения.")

    def update_tube_text(self, q=None, plotnost=None, error_message=None):
        """Обновляет текстовое поле с результатами или сообщением об ошибке."""
        self.tube_text.config(state="normal")
        self.tube_text.delete("1.0", tk.END)

        if error_message:
            self.tube_text.insert(tk.END, error_message)
        else:
            self.tube_text.insert(tk.END, f"Расход газа: {q:.2f}\n")
            self.tube_text.insert(tk.END, f"Плотность газа: {plotnost:.4f}\n")

        self.tube_text.config(state="disabled")




if __name__ == "__main__":
    filename =logger_config.create_log_file() 
    logger = logger_config.setup_logger(filename)
    data_model = Data_model(logger)

    model = Model(data_model)
    root = tk.Tk()
    app = GuiManager(root)
    controller =Сontroller(app.gas_composition_manager,model)
    
    

    root.mainloop()