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


class GuiManager:
    def __init__(self, root: tk.Tk, data_model:'Data_model',fulCalc,result,datasaverloader:'DataSaverLoader'):
        self.root = root
        self.data_model = data_model
        self.datasaverloader=datasaverloader
        self.fulCalc = fulCalc
        self.result = result
        self.style = ttk.Style(root)
        self._create_menu()
        self._create_style()
        self._create_notebook()



        # Инициализация менеджеров для каждой функциональности
        self.gas_composition_manager = GasCompositionManager(self.tabs["Исходные данные"], self.data_model)
        self.tempearure_manager = TemperatureManager(self.tabs["Исходные данные"], self.data_model)
        self.pressure_range_manager = PressureRangeManager(self.tabs["Исходные данные"], self.data_model)
        self.table_manager = TableManager(self.tabs["Исходные данные"],self.data_model)
        self.gas_properties_manager = GasPropertiesManager(self.tabs["Свойства газа"],self.data_model)
        self.tube_properties_manager = TubePropertiesManager(self.tabs["Расчет пропускной способности трубы"],self.data_model)
        self.regulatormanager = RegulatorManager(self.tabs["Расчет регулятора"],self.data_model)
        self.heatbalancemanager = HeatBalanceManager(self.tabs["Тепловой баланс"],self.data_model)

        self.root.title("Расчеты газовых систем")
        self.root.geometry("700x300")  # Начальный размер окна
        self.root.minsize(700, 300)     # Минимальный размер окна
        

    def _create_menu(self):
        self.root.option_add("*tearOff", FALSE)

        main_menu = Menu()

        file_menu = Menu()
        file_menu.add_command(label="Save",command=self.datasaverloader.save_data)
        file_menu.add_command(label="Open",command=self.datasaverloader.load_data)
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
        self.style.map("TButton", background=[("active", "#45a049")])
    
    def _create_notebook(self):   
        # Создаем Notebook с стилем
        self.notebook = ttk.Notebook(root, style="Custom.TNotebook")
        self.style.configure("Custom.TNotebook", tabposition="n", background="#e0e0e0")
        self.notebook.pack(fill="both", expand=True)

        # Создаем ссписок для названий вкладок расчетов
        tabs_name = ["Исходные данные", "Свойства газа", "Расчет пропускной способности трубы", "Расчет регулятора", "Тепловой баланс"]
        
        # Создаем словарь для хранения фреймов
        self.tabs = {}

        for name in tabs_name:
            frame = ttk.Frame(self.notebook)
            self.tabs[name] = frame  # Сохраняем фрейм в словаре
            self.notebook.add(frame, text=name)

        calculate_button = ttk.Button(self.tabs["Исходные данные"], text="Автоматический расчет", command= self.result.result_table)
        calculate_button.grid(row=7, column=0, padx=5, pady=5) #  Разместите кнопку на сетке
        
class WidgetFactory:  
    @staticmethod
    def create_entry(parent, row, column=1, padx=5, pady=5):
        entry = ttk.Entry(parent)
        entry.grid(row=row, column=column, padx=padx, pady=pady)
        return entry
    
    @staticmethod
    def create_label(parent, label_text, row, column=0, padx=5, pady=5):
        label = ttk.Label(parent, text=label_text)
        label.grid(row=row, column=column, padx=padx, pady=pady, sticky="w")
        return label
    
    @staticmethod
    def create_Button(parent, label_text, row, function, column=0, padx=5, pady=5):
        Button = ttk.Button(parent, text=label_text, command=function)
        Button.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
        return Button
    
class GasCompositionManager:
    def __init__(self, parent, data_model:'Data_model'):
        self.parent = parent
        self.data_model = data_model
        self.create_widgets()
        logger.info("GasCompositionManager инициализирован")

    def create_widgets(self):
        # Кнопка для ввода состава газа
        gas_button = WidgetFactory.create_Button(self.parent,label_text="Ввести состав газа", row=1,function=self.input_gas_composition)
        gaz_label = WidgetFactory.create_label(self.parent,"<--Обзательно к заполнению",row=1,column=1)


    def input_gas_composition(self):
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
        self.entries = {}
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
        self.load_gas_composition()

        # Кнопка для сохранения данных
        save_button = WidgetFactory.create_Button(self.gas_window, "Сохранить", self.row_last_components,(lambda :setattr(self.data_model, 'data_gas_composition', self.entries)))
    #Кнопка для сохранения в файл
        save_to_file_button = WidgetFactory.create_Button(
            self.gas_window,
            "Сохранить в файл",
            self.row_last_components+1,
            self.save_gas_composition_to_csv
        )

         #Кнопка для открытия из файла
        load_from_file_button = WidgetFactory.create_Button(
            self.gas_window,
            "Открыть из файла",
            self.row_last_components+2,
            self.load_gas_composition_from_csv
        )
    def update_total_percentage(self, event=None):
        """
        Подсчитывает сумму процентов из всех полей ввода и обновляет метку.
        """
        total = 0.0
        for component, entry in self.entries.items():
            try:
                value = float(entry.get())
                total += value
            except ValueError:
                pass  # Если значение некорректно, игнорируем его

        # Обновляем метку с суммой
        self.total_label.config(text=f"Сумма: {total:.4f}%")

    def load_gas_composition(self):

        """Loads the gas composition from the data model and updates the entry fields."""
        saved_composition = self.data_model.data_gas_composition
        for component, entry in self.entries.items():
            if component in saved_composition:
                entry.delete(0, tk.END)
                entry.insert(0, str(saved_composition[component]))
         # Обновляем сумму после загрузки данных
        self.update_total_percentage()

    def save_gas_composition_to_csv(self):
        """Saves the current gas composition to a CSV file."""

        try:
            # Открываем проводник для выбора пути и имени файла
            file_path = filedialog.asksaveasfilename(
                title="Сохранить состав газа как",
                defaultextension=".csv",  # Расширение по умолчанию
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]  # Фильтр типов файлов
            )

            if not file_path:  # Если пользователь отменил выбор
                logger.warning("Отмена.Сохранение отменено пользователем")
                showwarning("Отмена", "Сохранение отменено пользователем")
                return

            # Сохраняем данные в выбранный файл
            with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(["Component", "Percentage"])  # Заголовок таблицы

                for component, entry in self.entries.items():
                    try:
                        percentage = float(entry.get())  # Преобразуем значение в число
                        writer.writerow([component, percentage])
                    except ValueError:
                        writer.writerow([component, 0.0])  # Если значение некорректно, записываем 0.0

            # Уведомляем пользователя об успешном сохранении
            logger.info(f"Состав газа сохранен в файл: {file_path}")
            showinfo("Успех", f"Состав газа сохранен в файл: {file_path}")

        except Exception as e:
            logger.error("Ошибка", f"Не удалось сохранить в файл: {e}")
            # Обрабатываем ошибки при сохранении
            showwarning("Ошибка", f"Не удалось сохранить в файл: {e}")

    def load_gas_composition_from_csv(self):
        """Loads the gas composition from a CSV file and updates the entry fields."""

        try:
            # Открываем проводник для выбора файла
            file_path = filedialog.askopenfilename(
                title="Выберите файл для загрузки состава газа",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]  # Фильтр типов файлов
            )

            if not file_path:  # Если пользователь отменил выбор
                showwarning("Отмена", "Загрузка отменена пользователем")
                logger.warning("Отмена", "Загрузка отменена пользователем")
                return

            # Проверяем существование файла
            if not os.path.exists(file_path):
                showwarning("Ошибка", f"Файл {file_path} не найден.")
                logger.error("Ошибка", f"Файл {file_path} не найден.")
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
                        logger.warning(f"{loaded_composition[row["Component"]]} = 0.0")

                # Устанавливаем состав газа в модели и обновляем поля ввода
                self.data_model.set_gas_composition_from_file(loaded_composition)
                self.load_gas_composition()  # Обновляем поля ввода

            # Уведомляем пользователя об успешной загрузке
            showinfo("Успех", f"Состав газа загружен из файла: {file_path}")
            logger.info(f"Состав газа загружен из файла: {file_path}")

        except Exception as e:
            # Обрабатываем ошибки при загрузке
            logger.error("Ошибка", f"Не удалось загрузить из файла: {e}")
            showwarning("Ошибка", f"Не удалось загрузить из файла: {e}")

class TemperatureManager:
    def __init__(self, parent, data_model:'Data_model'):
        self.parent = parent
        self.data_model = data_model
        self.create_widgets()

    def create_widgets(self):
        """Создает кнопки для ввода температур."""
        button_temp = WidgetFactory.create_Button(
            parent=self.parent,
            label_text="Температура газа",
            row=2,
            function=self.temperature_dialog
        )

    def temperature_dialog(self):
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
        
        temperature = self.data_model.get_temperature()
        print(f"{temperature=}")
        if temperature:
            # min_pressure_entry.insert(0, min(pressure_range))

            self.entries_dict["input"].insert(0,temperature['in'])
            self.entries_dict["output"].insert(0,temperature['out'])
            
        save_button = WidgetFactory.create_Button(
            pressure_window,
            label_text="Сохранить",
            row=3,
            function=lambda: self.save_temperature(pressure_window)
        )

    def save_temperature(self, pressure_window):
        """Сохраняет температуры в Data_model."""
        try:
            # Проверка на пустые значения
            input_temp_str = self.entries_dict["input"].get().strip()
            output_temp_str = self.entries_dict["output"].get().strip()
            
            if not input_temp_str or not output_temp_str:
                raise ValueError("Оба поля должны быть заполнены")

            # Преобразование в числа
            input_temp = float(input_temp_str)
            output_temp = float(output_temp_str)

            # Проверка на отрицательные значения (пример)
            if input_temp < -273.15 or output_temp < -273.15:
                raise ValueError("Температура не может быть ниже абсолютного нуля (-273.15°C)")

            # Сохранение данных
            self.data_model.set_temperature(input_temp, output_temp)
            logger.info("Температуры успешно сохранены: вход = %s°C, выход = %s°C", input_temp, output_temp)
            showinfo("Успех", "Данные успешно сохранены!")
            pressure_window.destroy()

        except ValueError as e:
            logger.error("Ошибка ввода температуры: %s", str(e))
            showinfo("Ошибка", f"Некорректные данные: {str(e)}")
        except Exception as e:
            logger.exception(f"Неожиданная ошибка при сохранении температуры {str(e)}")
            showinfo("Ошибка", "Произошла непредвиденная ошибка. Проверьте логи.")

class PressureRangeManager:
    def __init__(self, parent, data_model:'Data_model'):
        self.parent = parent  # Окно
        self.data_model = data_model  # Передаем класс для расчета
        self.create_widgets()

    def create_widgets(self):
        """
        Создает кнопки для ввода диапазонов давлений.
        """
        for idx, (title, label) in enumerate([("input", "Указать диапазон входных давлений"),
                                             ("output", "Указать диапазон выходных давлений")]):
            button = ttk.Button(self.parent, text=label,
                                command=lambda t=title: self.input_pressure_range_dialog(t))
            button.grid(row=3 + idx, column=0, padx=10, pady=5, sticky="ew")

    def input_pressure_range_dialog(self, title):
        """
        Открывает диалоговое окно для ввода диапазона давлений.
        """
        pressure_window = tk.Toplevel(self.parent)
        pressure_window.title(title)

        labels = ["Минимальное давление:", "Максимальное давление:", "Шаг значения"]
        entries = []

        for i, label_text in enumerate(labels):
            ttk.Label(pressure_window, text=label_text).grid(row=i, column=0, padx=5, pady=5)
            entry = WidgetFactory.create_entry(pressure_window, row=i, column=1)
            entries.append(entry)

        min_pressure_entry, max_pressure_entry, average_value_entry = entries
    
        # Загрузка предыдущих значений
        pressure_range = getattr(self.data_model, f"get_{title.lower()}_pressure_range")()
        if pressure_range:
            min_pressure_entry.insert(0, min(pressure_range))
            max_pressure_entry.insert(0, max(pressure_range))
            average_value_entry.insert(0, pressure_range[1] - pressure_range[0])

        save_button = ttk.Button(
            pressure_window, text="Сохранить",
            command=lambda: self.save_pressure_range(
                title, min_pressure_entry.get(), max_pressure_entry.get(),
                average_value_entry.get(), pressure_window
            )
        )
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def _calculate_pressure_range(self, min_pressure_entry, max_pressure_entry, average_value_entry)-> List[float]:
        try:
            # Проверка на пустые значения

            if not all([min_pressure_entry.strip(), max_pressure_entry.strip(), average_value_entry.strip()]):
                raise ValueError("Ошибка: Введите значения")

            # Преобразуем входные данные в числа
            min_pressure = float(min_pressure_entry)
            max_pressure = float(max_pressure_entry)
            average_value = float(average_value_entry)

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
    
    def save_pressure_range(self, title, min_pressure, max_pressure, average_value, window):
        """
        Сохраняет диапазон давлений.
        """
        try:
            pressure_type = title.lower()
            set_pressure_range=self._calculate_pressure_range(min_pressure, max_pressure, average_value)

            self.data_model.set_pressure_range(pressure_type,set_pressure_range)
            window.destroy()
            logger.info(f"Диапазоны {pressure_type} давления  успешно сохранены: максимальное = %s мПа, минимальное = %s мПа,шаг = %s", max_pressure, min_pressure,average_value)
        except ValueError:
            logger.warning("Введите корректные числовые значения!")
            showwarning("Ошибка", "Введите корректные числовые значения!")

class BaseTableManager(ABC):
    def __init__(self,parent,data_model:'Data_model',table_type):
        self.parent = parent
        self.data_model = data_model
        self.db_path = "tables.db"  # Путь к файлу базы данных SQLite
        self.table_type = table_type

    @abstractmethod
    def get_columns(self) -> list:
        pass
    
    def get_table_type(self):
        return self.table_type
    
    def create_table(self,table_name):
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
        
    def load_table(self, table_name):
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

    def save_data(self, tree, table_name,window):
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

    def open_table_window(self, table_name):
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
    def create_table_manager(table_type, parent, data_model):
        logger.info(f"Запрос на создание менеджера таблицы типа: '{table_type}'")
        logger.debug(f"Параметры: parent={parent}, data_model={data_model}")

        match table_type:
            case "Таблица для регуляторов":
                logger.info("Создан менеджер таблицы регуляторов")
                return RegulatorTableManager(parent, data_model,table_type)
            
            case "Таблица котельной":
                logger.info("Создан менеджер таблицы котельной")
                return BoilerTableManager(parent, data_model,table_type)
            
            case "Таблицы для труб до регулятора" | "Таблицы для труб после регулятора":
                logger.info(f"Создан менеджер таблицы труб: {table_type}")
                return PipeTableManager(parent, data_model,table_type)
            
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
                label = WidgetFactory.create_label(
                    self.table_window,
                    self.tables[name][1],
                    self.row
                )
                entry = WidgetFactory.create_entry(self.table_window, self.row, 1)
                entry.insert(0, name)
                open_button = WidgetFactory.create_Button(
                    self.table_window,
                    "Открыть таблицу",
                    self.row,
                    lambda tn=name, tt=self.tables[name][1]: self.open_table(tn, tt),
                    3
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
        manager = TableFactory.create_table_manager(table_type, self.parent, self.data_model)
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

    def save_table(self, table_name):
        logger.info(f"Попытка сохранения таблицы '{table_name}'")
        if table_name in self.tables:
            logger.debug("Сохранение данных через менеджер таблицы")
            self.tables[table_name][0].save_data(
                self.tables[table_name][0].tree,
                table_name
            )
        else:
            logger.error(f"Таблица '{table_name}' не найдена")
            messagebox.showerror("Ошибка", f"Таблица '{table_name}' не найдена!")

class GasPropertiesManager:
    def __init__(self, parent,data_model:'Data_model'):
        self.parent = parent
        self.data_model = data_model
        self.create_widgets()
        self.list = []

    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать",2, self.start)

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

        gas_composition = self.data_model.data_gas_composition  # Получаем состав газа
        rho_rab, z, plotnost,Di,Ccp = Calculate_file.data_frame(p_in, t_in, gas_composition)

        # self.data_model.set_gas_properties([rho_rab, z, plotnost,Di,Ccp])

        self.gaz_text.config(state="normal")
        self.gaz_text.delete("1.0", tk.END)
        self.gaz_text.insert(tk.END, f"=== Введенные данные ===\nДавление: {p_in}\nТемпература: {t_in}\n")
        self.gaz_text.insert(tk.END, f"Плотность смеси при рабочих условиях: {rho_rab:.2f} кг/м3 \n")
        self.gaz_text.insert(tk.END, f"Коэффициент сжимаемости: {z}\n")
        self.gaz_text.insert(tk.END, f"Плотность смеси при стандартных условиях: {plotnost:.4f} кг/м3 ")
        self.gaz_text.config(state="disabled")

class TubePropertiesManager:
    
    def __init__(self, parent,data_model:'Data_model'):
        self.parent = parent
        self.data_model = data_model
        self.entries = {}
        self.create_widgets()
        
    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(
            self.parent, "Расчитать", 0, self.calc_tube
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
 
class RegulatorManager:
    def __init__(self, parent,data_model):
        self.parent = parent
        self.data_model = data_model
        self.entries = {}
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать",9, self.calc_regul)
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

class HeatBalanceManager:
    def __init__(self, parent,data_model):
        self.parent = parent
        self.data_model = data_model
        self.entries = {}
        self.create_widgets()
    
    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать",9, self.calc_heat_balance)
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

class Max_performance:
    def __init__(self,data_model:Data_model,save_result):
        self.data_model = data_model
        self.save_result = save_result

    def get_data(self):# берем остольные данные из class Data Model
        self.input_pressure_range = self.data_model.get_input_pressure_range() #Диапазон входного давления
        self.output_pressure_range = self.data_model.get_output_pressure_range() #Диапазон выходного давления
        self.tables_data = self.data_model.get_table_manager() # Названия таблиц

    def calculate_tube(self,col_pressure, data, df, col_name,table_name):
        _, z, *_ = self.calculate_propertys_gaz(col_pressure, data["gas_temperature"])
        df.at[table_name, col_name] = float(Calculate_file.calc(
                data["pipe_diameter"], # Диаметр трубы
                data["wall_thickness"], # Толщина стенки
                col_pressure, # Давление на входе
                data["gas_temperature"], # Температура газа
                data["gas_speed"], # Скорость газа
                data["lines_count"], # Количество линий
                z
                 ))
                 

    def calculate_regulator(self,col_pressure, p_out, data, df, col_name,table_name):
        *_,plotnost,Di_in,_= self.calculate_propertys_gaz(col_pressure, float(self.data_model.get_temperature()["in"]))
        df.at[table_name, col_name] = float(Calculate_file.calculate_Ky(
                col_pressure,
                p_out,
                float(self.data_model.get_temperature()["in"]),
                plotnost,
                data["kv"],
                data["lines_count"],
                True,
                float(self.data_model.get_temperature()["out"]),
                Di_in
                ))

    def calculate_heat_balance(self,col_pressure, p_out, data, df, col_name,table_name):
        
        *_,Di_in,Ccp_in = self.calculate_propertys_gaz(col_pressure,float(self.data_model.get_temperature()["in"])) #получаем свойства газа
        # *_, Ccp_out = self.calculate_propertys_gaz(p_out,float(self.data_model.get_temperature()["out"])) #получаем свойства газа
      
        df.at[table_name, col_name] = Calculate_file.heat_balance(
            col_pressure, # Давление на входе
            p_out, # Давление на выходе
            float(self.data_model.get_temperature()["in"]),
            float(self.data_model.get_temperature()["out"]),
            data["boiler_power"], # Мощность котла
            Di_in,
            Ccp_in,
            True
            )

    def calculate_propertys_gaz(self,gas_pressure_mpa,gas_temperature_c):
        gas_composition = self.data_model.data_gas_composition # Получаем состав газа
        rho_rab, z, plotnost,Di,Ccp = Calculate_file.data_frame(gas_pressure_mpa, gas_temperature_c, gas_composition)
        return  rho_rab, z, plotnost,Di,Ccp
    
    def full_calculate(self, P_out: float) -> pd.DataFrame:
        logger.info(f"*** Начинаем полный расчет для P_out={P_out} МПа ***")

        try:
            # Получение данных из модели
            logger.debug("Загрузка данных из DataModel")
            self.get_data()
            logger.info(f"Диапазон входных давлений: {self.input_pressure_range}")
            logger.info(f"Диапазон выходных давлений: {self.output_pressure_range}")
            logger.info(f"Таблицы для расчета: {self.tables_data}")

            # Создаем пустой DataFrame
            df = pd.DataFrame()
            logger.debug("Создан пустой DataFrame для результатов")

            # Обрабатываем каждую таблицу
            for table_name, table_info in self.tables_data.items():
                table_type = table_info[1]
                logger.info(f"Обрабатываем таблицу '{table_name}' типа '{table_type}'")

                # Получаем данные таблицы
                data = self.data_model.get_data_table(table_name)
                logger.debug(f"Данные таблицы '{table_name}': {data}")

                # Итерация по входным давлениям
                input_pressures = [float(p) for p in self.input_pressure_range]
                for col_pressure in input_pressures:
                    logger.info(f"Обработка давления {col_pressure} МПа для таблицы '{table_name}'")
                    col_name = f"Pin_{str(col_pressure).replace('.', '_')}"
                    
                    try:
                        match table_type:
                            case "Таблица для регуляторов":
                                logger.info("Начинаем расчет регулятора")
                                self.calculate_regulator(col_pressure, P_out, data, df, col_name, table_name)
                                logger.debug(f"Результат регулятора: {df.loc[table_name, col_name]}")

                            case "Таблицы для труб до регулятора":
                                logger.info("Начинаем расчет труб до регулятора")
                                self.calculate_tube(col_pressure, data, df, col_name, table_name)
                                logger.debug(f"Результат труб до регулятора: {df.loc[table_name, col_name]}")

                            case "Таблицы для труб после регулятора":
                                logger.info("Начинаем расчет труб после регулятора")
                                self.calculate_tube(P_out, data, df, col_name, table_name)
                                logger.debug(f"Результат труб после регулятора: {df.loc[table_name, col_name]}")

                            case "Таблица котельной":
                                logger.info("Начинаем расчет теплового баланса")
                                self.calculate_heat_balance(col_pressure, P_out, data, df, col_name, table_name)
                                logger.debug(f"Результат теплового баланса: {df.loc[table_name, col_name]}")

                    except Exception as e:
                        logger.error(f"Ошибка при обработке давления {col_pressure} для таблицы '{table_name}': {str(e)}")
                        logger.exception(e)

            logger.info(f"Итоговый DataFrame: \n{df.to_string()}")
            
            # Формируем минимальные значения
            df_min = pd.DataFrame([df.min()])
            logger.info(f"Минимальные значения для P_out={P_out}: \n{df_min.to_string()}")
            
            # Сохраняем промежуточный результат
            self.save_result.save(df, f"Промежуточный результат для P_out={P_out}")
            logger.info(f"Промежуточные результаты сохранены для P_out={P_out}")
            
            return df_min

        except Exception as e:
            logger.error(f"Критическая ошибка в full_calculate: {str(e)}")
            logger.exception(e)
            raise

class Result:
    def __init__(self, data_model:Data_model, max_performance, save_result):
        self.data_model = data_model
        self.max_performance = max_performance
        self.save_result = save_result
        logger.debug("Инициализация Result")

    def get_data(self):
        logger.info("Получение данных из DataModel")
        self.output_pressure = self.data_model.get_output_pressure_range()
        logger.debug(f"Полученные выходные давления: {self.output_pressure}")

    def result_table(self):
        logger.info("***** Начало формирования результирующей таблицы *****")
        try:
            df_result = pd.DataFrame()
            logger.debug("Создан пустой DataFrame для итоговых результатов")
            
            self.get_data()  # Загружаем выходные давления
            
            for out_pressure in self.output_pressure:
                logger.info(f"Обработка выходного давления: {out_pressure} МПа")
                
                # Расчет минимальных значений
                df_min = self.max_performance.full_calculate(out_pressure)
                logger.debug(f"Результат full_calculate для {out_pressure=}: \n{df_min.to_string()}")
                
                # Установка индекса
                df_min.index = [out_pressure] * len(df_min)
                logger.debug(f"Индекс установлен: {df_min.index.tolist()}")
                
                # Объединение с итоговой таблицей
                df_result = pd.concat([df_result, df_min])
                logger.debug(f"Текущий df_result после добавления данных: \n{df_result}")

            # Сохранение результата
            self.save_result.save(df_result, "Результирующая таблица")
            logger.info(f"Сохранена результирующая таблица: \n{df_result}")
            
       
            df_result.to_excel("output.xlsx", index=True)
            logger.info(f"Сохранена результирующая таблица в EXEL: \n{df_result}")
           

            # Построение графика
            logger.info("Начало построения графика")
            plt.figure(figsize=(10, 6))
            
            input_pressures = [i.replace("Pin_", "") for i in df_result.columns]
            logger.debug(f"Ось X (входные давления): {input_pressures}")
            
            output_pressures = df_result.index.tolist()
            logger.debug(f"Ось Y (выходные давления): {output_pressures}")

            for output_pressure in output_pressures:
                logger.debug(f"Построение линии для выходного давления: {output_pressure}")
                plt.plot(
                    input_pressures, 
                    df_result.loc[output_pressure], 
                    label=f"Выходное давление {output_pressure}"
                )
            
            # Настройка графика
            plt.title("График зависимости расхода от входного давления")
            plt.xlabel("Входное давление (МПа)")
            plt.ylabel("Расход")
            plt.legend(title="Выходное давление")
            plt.grid(True)
            
            logger.info("График успешно построен. Отображение...")
            plt.show()
            
        except Exception as e:
            logger.error(f"Критическая ошибка в result_table: {str(e)}")
            logger.exception(e)
            messagebox.showerror("Ошибка", f"Ошибка формирования таблицы/графика: {e}")
        finally:
            logger.info("***** Формирование результирующей таблицы завершено *****")

class Save_intermediate_result:
    def __init__(self):
        self.db_path = "tables.db"  # Путь к файлу базы данных SQLite
        
    def save(self,df,name_P_out):
        column = df.columns.tolist()
        # Формируем SQL-определение столбцов
        column_definitions = ", ".join([f"{col} REAL" for col in column])
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # cursor.execute(f"DELETE FROM {name_P_out}")  # Очистка таблицы
            # create_table_query = (f"CREATE TABLE IF NOT EXISTS {name_P_out} ({column_definitions})")
            # cursor.execute(create_table_query)
            # Добавляем данные из DataFrame
            df.to_sql(name_P_out, conn, if_exists="replace", index=True)
        logger.info(f"Промежуточная таблица {name_P_out=} сохранена в базе данных")

class DataSaverLoader:
    def __init__(self,data_model:Data_model):
        self.data_model = data_model
        self.input_pressure_range = []
        self.output_pressure_range = []
        self.gas_composition = {}
        self.name_table = {}
        self.temperature = []

    def update_data(self):
        # Используем деструктуризацию для получения данных
        self.input_pressure_range = self.data_model.get_input_pressure_range()
        self.output_pressure_range = self.data_model.get_output_pressure_range()
        self.gas_composition = self.data_model.data_gas_composition
        self.temperature = self.data_model.get_temperature()
        # Обработка таблиц
        self.name_table = self.data_model.get_table_manager()
        self.table_name = {key: manager.get_table_type() for key, manager in self.name_table.items()}
        
    def to_dict(self):
        return {
            "gas_composition": self.gas_composition,
            "input_pressure_range": self.input_pressure_range,
            "output_pressure_range": self.output_pressure_range,
            "temperature": self.temperature,
            "table_name": self.table_name
        }
    
    def save_data(self):
        saves_dir = "Saves"
        os.makedirs(saves_dir, exist_ok=True)  # Создаем директорию, если её нет
        self.update_data()
        data_dict = self.to_dict()
        file_path = filedialog.asksaveasfilename(
                title="Сохранить файл",
                initialdir = saves_dir,
                defaultextension=".json",  # Расширение по умолчанию
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]  # Фильтр типов файлов
            )
        with open(file_path, 'w',encoding='utf-8') as outfile:
            json.dump(data_dict, outfile, indent=4, ensure_ascii=False)

    def load_data(self):
        file_path = filedialog.askopenfilename(
                title="Выберите файл для загрузки состава газа",
                defaultextension=".json",  # Расширение по умолчанию
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]  # Фильтр типов файлов
            )
        with open(file_path, 'r',encoding='utf-8') as outfile:
            data = json.load( outfile)
            # print(data["gas_composition"])
            print(data["input_pressure_range"])
            # print(data["output_pressure_range"])
            # # print(data["temperature"]["in"])
            # print(data["table_name"])

        # self.data_model.set_temperature(data["temperature"]["in"],data["temperature"]["out"])
        # self.data_model.data_gas_composition = data["gas_composition"]
        # print(f"{self.data_model.data_gas_composition=}")
    
        
        self.data_model.set_pressure_range("input",data["input_pressure_range"])
        self.data_model.set_pressure_range("output",data["output_pressure_range"])
        print(f"{self.data_model.get_input_pressure_range()=}")
        print(f"{self.data_model.get_output_pressure_range()=}")
        # print(f"{self.data_model.get_temperature()=}")
        pass



if __name__ == "__main__":
    
    # Настройка логгера
    filename =logger_config.create_log_file() 
    logger = logger_config.setup_logger(filename)
    
    save_result = Save_intermediate_result()
    root = tk.Tk()
    data_model = Data_model(logger)
    datasaverloader = DataSaverLoader(data_model)
    fulCalc = Max_performance(data_model,save_result)
    result =Result(data_model,fulCalc,save_result)
    app = GuiManager(root, data_model,fulCalc,result,datasaverloader)
    
    root.mainloop()
    