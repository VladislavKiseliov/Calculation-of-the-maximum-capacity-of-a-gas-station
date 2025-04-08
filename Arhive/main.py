import tkinter as tk
from tkinter import ttk,filedialog
import math
from tkinter.messagebox import showwarning, showinfo
import Calculate_file
import numpy as np
import pandas as pd
import os  # Import the 'os' module
import csv
import sqlite3
from typing import List, Dict, Any,Optional,TypedDict
import logger_config 
import datetime
import matplotlib.pyplot as plt



class GuiManager:
    def __init__(self, root, data_model,fulCalc,result):
        self.root = root
        self.data_model = data_model
        self.fulCalc = fulCalc
        self.result = result
        self.style = ttk.Style(root)

        root.title("Расчеты газовых систем")
        root.geometry("700x300")  # Начальный размер окна
        root.minsize(700, 300)     # Минимальный размер окна

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
        
        # Создаем Notebook с стилем
        self.notebook = ttk.Notebook(root, style="Custom.TNotebook")
        self.style.configure("Custom.TNotebook", tabposition="n", background="#e0e0e0")
        self.notebook.pack(fill="both", expand=True)

        # Создаем фреймы для каждой вкладки
        self.tab1 = ttk.Frame(self.notebook)  # Исходные данные
        self.tab2 = ttk.Frame(self.notebook)  # Свойства газа
        self.tab3 = ttk.Frame(self.notebook)  # Расчет пропускной способности трубы
        self.tab4 = ttk.Frame(self.notebook)  # Расчет регулятора
        self.tab5 = ttk.Frame(self.notebook)  # Расчет регулятора

        # Добавляем фреймы в Notebook как вкладки
        self.notebook.add(self.tab1, text="Исходные данные")
        self.notebook.add(self.tab2, text="Свойства газа")
        self.notebook.add(self.tab3, text="Расчет пропускной способности трубы")
        self.notebook.add(self.tab4, text="Расчет регулятора")
        self.notebook.add(self.tab5, text="Тепловой баланс")

        # Инициализация менеджеров для каждой функциональности
        self.gas_composition_manager = GasCompositionManager(self.tab1, self.data_model)
        self.tempearure_manager = TemperatureManager(self.tab1, self.data_model)
        self.pressure_range_manager = PressureRangeManager(self.tab1, self.data_model)
        self.table_manager = TableManager(self.tab1,self.data_model)
        self.gas_properties_manager = GasPropertiesManager(self.tab2,self.data_model)
        self.tube_properties_manager = TubePropertiesManager(self.tab3,self.data_model)
        self.regulatormanager = RegulatorManager(self.tab4,self.data_model)
        self.heatbalancemanager = HeatBalanceManager(self.tab5,self.data_model)

        calculate_button = ttk.Button(self.tab1, text="Автоматический расчет", command= self.result.result_table)
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
    def __init__(self, parent, data_model):
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
            "Моноксид углерода: CO", "Азот: N2", "Кислород: O2", "Диоксид углерода: CO2"
        ]

        # Создаем метки и поля ввода для каждого компонента
        self.entries = {}
        for i, component in enumerate(self.components):
            if i <=(len(self.components)/2.0):
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
        save_button = WidgetFactory.create_Button(self.gas_window, "Сохранить", self.row_last_components,(lambda : self.data_model.set_gas_composition(self.entries,self.gas_window)))
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
        saved_composition = self.data_model.get_gas_composition()
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
                logger.warning("Отмена", "Сохранение отменено пользователем")
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
    def __init__(self, parent, data_model):
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
    def __init__(self, parent, data_model):
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

    def save_pressure_range(self, title, min_pressure, max_pressure, average_value, window):
        """
        Сохраняет диапазон давлений.
        """
        try:
            pressure_type = title.lower()
            self.data_model.set_pressure_range(pressure_type,min_pressure, max_pressure, average_value,window)
            logger.info(f"Диапазоны {pressure_type} давления  успешно сохранены: максимальное = %s мПа, минимальное = %s мПа,шаг = %s", max_pressure, min_pressure,average_value)
        except ValueError:
            logger.warning("Введите корректные числовые значения!")
            showwarning("Ошибка", "Введите корректные числовые значения!")

class TableManager:
    def __init__(self, parent,data_model):
        self.parent = parent
        self.data_model = data_model
        self.db_path = "tables.db"  # Путь к файлу базы данных SQLite
        self.create_widgets()
        self.row = 3
        self.table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной",
            "Таблицы для труб до регулятора",
            "Таблицы для труб после регулятора"
        ]
        self.columns = []
        self.check_table = {} #для проверки сущестующих таблиц

    def create_widgets(self):
        # Кнопка для ввода исходных таблиц
        input_table_button = ttk.Button(self.parent, text="Исходные таблицы", command=self.check_table_func)
        input_table_button.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

    def create_input_table(self):
        
        # Окно для выбора таблицы
        self.table_window = tk.Toplevel(self.parent)
        self.table_window.title("Количество исходных таблиц")
      

        # Метка для выбора таблицы
        label = WidgetFactory.create_label(self.table_window,"Выберите таблицу:",0)

        # Combobox для выбора таблицы
        self.combobox = ttk.Combobox(self.table_window, values=self.table_labels, state="readonly",width=33)
        self.combobox.grid(row=1, column=0, padx=5, pady=5)

        # Кнопка для добавления таблицы
        save_button = WidgetFactory.create_Button(self.table_window, "Добавить таблицу",2, self.create_table)

    def check_table_func(self):
        if len(self.check_table) == 0:
            self.create_input_table()
        else:
            self.create_input_table()
            for key,value in self.check_table.items():
                label = WidgetFactory.create_label(self.table_window,value, self.row) 
                entry =  WidgetFactory.create_entry(self.table_window, self.row, 1) 
                entry.insert(0, key)
                open_button = WidgetFactory.create_Button(self.table_window,"Открыть таблицу", self.row,(lambda :self.open_table1(value, entry.get())),3)
                self.row += 1

    def create_table(self):
        """Создание таблицы в базе данных."""
        selection = self.combobox.get()
        if not selection:
            print("Ошибка: Таблица не выбрана!")
            return
        self.row += 1
        # Метка с названием таблицы
        label = WidgetFactory.create_label(self.table_window,label_text=selection,row=self.row)

        # Поле ввода для имени таблицы
        entry = WidgetFactory.create_entry(self.table_window,row=self.row,column=1)

        # Кнопка для открытия таблицы
        open_button = WidgetFactory.create_Button(self.table_window,
                                                label_text="Открыть таблицу",
                                                row=self.row,
                                                function=lambda : self.open_table1(selection, entry.get()),
                                                column=3)
    
    def create_sql_table(self,table_name,type_table):
        table_name1 = f"{table_name}"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            match type_table:
                case "Таблица для регуляторов":
                    cursor.execute(f'''
                            CREATE TABLE IF NOT EXISTS {table_name1} (
                                regulator TEXT,
                                kv REAL,
                                lines_count INTEGER
                            )
                        ''')
                    cursor.execute(f'''
                            insert into {table_name1} (regulator, kv, lines_count) values ( "","" , "")
                        ''')
                    self.check_table[table_name1] = type_table
                case "Таблица котельной":
                    cursor.execute(f'''
                                    CREATE TABLE IF NOT EXISTS {table_name1} (
                                        boiler_power REAL,
                                        gas_temp_in REAL,
                                        gas_temp_out REAL
                                    )
                                ''')
                    cursor.execute(f'''
                            insert into {table_name1} (boiler_power, gas_temp_in, gas_temp_out) values ( "","" , "")
                        ''')
                    self.check_table[table_name1] = type_table

                case "Таблицы для труб до регулятора" :
                    cursor.execute(f'''
                                    CREATE TABLE IF NOT EXISTS {table_name1} (
                                        pipe_diameter REAL,
                                        wall_thickness REAL,
                                        gas_temperature_c REAL,
                                        gas_speed REAL,
                                        lines_count INTEGER
                                    )
                                ''')
                    cursor.execute(f'''
                            insert into {table_name1} (pipe_diameter, wall_thickness,gas_temperature_c, gas_speed,lines_count) values ( "","" ,"", "","")
                        ''')
                    self.check_table[table_name1] = type_table
                case  "Таблицы для труб после регулятора":
                    cursor.execute(f'''
                                    CREATE TABLE IF NOT EXISTS {table_name1} (
                                        pipe_diameter REAL,
                                        wall_thickness REAL,
                                        gas_temperature_c REAL,
                                        gas_speed REAL,
                                        lines_count INTEGER
                                    )
                                ''')
                    cursor.execute(f'''
                            insert into {table_name1} (pipe_diameter, wall_thickness,gas_temperature_c, gas_speed,lines_count) values ( "","" ,"", "","")
                        ''')
                    self.check_table[table_name1] = type_table

        logger.info(f"Таблица с именем <<{table_name1}>> и типом <<{type_table}>> сохранена в базе данных")

    def open_table1(self, table_type, table_name):
        table_name_1 = f"{table_name}"
        """Открытие таблицы в новом окне."""
        if not table_name:
            print("Ошибка: Название таблицы не введено!")
            return
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            # Создаем таблицы, если они не существуют
            cursor.execute('''
               SELECT name FROM sqlite_master WHERE type='table'
            ''')
            self.tables_name = cursor.fetchall()
            logger.info(f"Существуюище таблицы <<{self.tables_name}>>")


        self.tables_name = [i[0] for i in self.tables_name]

        if table_name_1 in self.tables_name:
            self.open_table(table_name,table_type)
            logger.info(f"Таблица была открыта из базы данных с именем <<{table_name}>> и типом <<{table_type}>>")

        else:
            self.create_sql_table(table_name,table_type)
            self.open_table(table_name_1,table_type)

    def open_table(self,table_name,table_type):
        """Открытие таблицы в новом окне."""
        new_window = tk.Toplevel(self.parent)
        new_window.title(f"Таблица: {table_name}")

        # Создаем фрейм для таблицы
        frame = tk.Frame(new_window)
        frame.pack(fill="both", expand=True)

        # Отображение данных из базы данных
        self.columns = self.get_columns(table_type)
        self.tree = ttk.Treeview(frame, columns=self.columns, show="headings")
        
        for col in self.columns:
            self.tree.heading(col, text=col)
        self.tree.pack(fill="both", expand=True)
        
        # Загрузка данных из базы данных

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table_name}")
            self.rows = cursor.fetchall()
            print(self.rows)

        for row in self.rows:
            self.tree.insert("", "end", values=row)

        # Кнопка для сохранения данных
        save_button = ttk.Button(
            new_window,
            text="Сохранить данные",
            command=lambda: self.save_data(self.tree, table_type, table_name)
        )
        save_button.pack(pady=10)
        self.tree.bind("<Double-1>", self.on_double_click)

    def on_double_click(self, event):
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

    def get_columns(self, table_type):
        """Получение столбцов для таблицы."""
        match table_type:
            case "Таблица для регуляторов":
                return ["Имя регулятора", "kv", "Количество линий"]
            case "Таблица котельной":
                return ["Мощность котельной", "Температура газа на входе", "Температура газа на выходе"]
            case "Таблицы для труб до регулятора" | "Таблицы для труб после регулятора":
                return ["Диаметр трубы", "Толщина стенки", "Скорость газа","Температура газа", "Количество линий"]
            case _:
                logger.error(f"Ошибка: Неизвестный тип таблицы <<{table_type}>>")
                print(f"Ошибка: Неизвестный тип таблицы '{table_type}'")
                return []

    def save_data(self, tree, table_type, table_name):
        """Сохранение данных в базу данных."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            table_name_sql = table_name
            cursor.execute(f"DELETE FROM {table_name_sql}")  # Очистка таблицы

            for item in tree.get_children():
                values = tree.item(item)["values"]
                placeholders = ",".join(["?"] * len(values))
                cursor.execute(
                    f"INSERT INTO {table_name_sql} VALUES ({placeholders})",
                    values)

        logger.info(f"Данные для таблицы <<{table_name}>> сохранены.")
        logger.info(f"Сохраняем в data_model <<{self.check_table=}>>")
        self.data_model.set_tables_data(self.check_table)

class GasPropertiesManager:
    def __init__(self, parent,data_model):
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

        gas_composition = self.data_model.get_gas_composition()  # Получаем состав газа
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
    
    def __init__(self, parent,data_model):
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
            gas_composition = self.data_model.get_gas_composition()

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

class Data_model:
    """Stores and manages application data.
    This class provides a centralized location for storing and retrieving
    various data used in the application, such as gas composition,
    pressure ranges, table data, and gas properties.
    """
    def __init__(self):
        self.gas_composition = {}
        self.input_pressure_range = []
        self.output_pressure_range = None
        self.tables_data = {}
        self.gas_properties = {}
        self.db_path = "tables.db"

    def get_gas_composition(self):
        return self.gas_composition

    def set_gas_composition(self, composition,gas_window):
        # Сохраняем введенные данные
        total_percentage = 0.0
        self.gas_composition = {} #Очищаем словарь, что бы не накладывало значения
        for component, entry in composition.items():
            try:
                percentage = float(entry.get())
                if percentage < 0:
                    raise ValueError("Отрицательное значение")
                self.gas_composition[component] = percentage
                total_percentage += percentage
            except ValueError:
                self.gas_composition[component] = 0.0  # Если введено неверное значение, считаем 0%

        # Проверяем, что сумма процентов равна 100%
        if abs(total_percentage - 100.0) > 0.001:  # Допускаем небольшую погрешность
            print(f"{abs(total_percentage - 100.0)=}")
            logger.error("Ошибка", f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.4f}%")
            showwarning("Ошибка", f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.4f}%")
            return 

        else:
            showinfo("Успех", "Данные успешно сохранены!")
            logger.info("Состав газа сохранен")
            print(self.gas_composition)
        gas_window.destroy()
        
    def set_gas_composition_from_file(self, loaded_composition):
        """
        Sets the gas composition from a loaded dictionary.

        Args:
            loaded_composition (dict): The dictionary of loaded gas composition data.
        """
        self.gas_composition = loaded_composition
        logger.info(f"Состав газа установлен из файла: {self.gas_composition}")
        print(f"Состав газа установлен из файла: {self.gas_composition}")    
    
    def get_input_pressure_range(self):
        return self.input_pressure_range

    def get_output_pressure_range(self):
        return self.output_pressure_range

    def _calculate_pressure_range(self, min_pressure_entry, max_pressure_entry, average_value_entry):
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

    def set_pressure_range(self, pressure_type, min_pressure_entry, max_pressure_entry, average_value_entry,window):
        """
        Устанавливает диапазон давлений (входного или выходного).
        :param pressure_type: "input" для входного давления, "output" для выходного.
        """
        try:
            pressure_range = self._calculate_pressure_range(min_pressure_entry, max_pressure_entry, average_value_entry)
        # Если диапазон не сгенерирован (ошибка), прерываем выполнение
            if pressure_range is None:
                logger.error(f"Диапазон {pressure_type} давлений не был сгенерирован")
                return  # Не закрываем окно и не выводим сообщение
            
            # Если всё успешно
            setattr(self, f"{pressure_type}_pressure_range", pressure_range)
            logger.info(f"Данные диапазона {pressure_type} давления сохранены")

            print(getattr(self, f"{pressure_type}_pressure_range"))
            showinfo("Успех", "Данные успешно сохранены!")
            window.destroy()  # Закрываем окно

        except Exception as e:
            logger.error(f"Не удалось сохранить данные: {e}")
            showwarning("Ошибка", f"Не удалось сохранить данные: {e}")

    def get_tables_data(self):
        """Возвращаем название и тип таблиц"""
        return self.tables_data

    def get_data_table(self,name_table) -> List[Dict[str, Any]]: 
        """Получение данных из базы данных."""
        with sqlite3.connect(self.db_path) as conn:
            df = pd.read_sql_query(f"SELECT * FROM {name_table}", conn)
            # print(f"{df.to_dict(orient="records")[0]=}")
            logger.info(f"Данные таблицы {name_table} полученны из баззы данных")
        return df.to_dict(orient="records")[0]  # Список словарей

    def set_tables_data(self, tables):
        self.tables_data = tables
        print(self.tables_data)
        logger.info(f"Данные таблицы {self.tables_data} добавлены в Data_model")
    
    def get_gas_properties(self):
        return self.gas_properties

    def set_gas_properties(self, gas_properties):
        self.gas_properties = gas_properties
        logger.info(f"Данные свойств газа {self.gas_properties} сохранены в Data_model")

    
    def set_temperature(self,temp_in,temp_out):
        self.temperature = {"in":temp_in,"out":temp_out}
        logger.info(f"Данные температуры газа {self.temperature} сохранены в Data_model")

    def get_temperature(self):
        return self.temperature

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
            gas_composition = self.data_model.get_gas_composition()  # Получаем состав газа
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
            gas_composition = self.data_model.get_gas_composition()  # Получаем состав газа
            rho_rab_in, z_in, plotnost_in,Di_in,Cc_in = Calculate_file.data_frame(input_values["Давление вход, МПа"], input_values["Температура вход, ℃"], gas_composition)
            rho_rab_out, z_out, plotnost_out,Di_out,Ccp_out = Calculate_file.data_frame(input_values["Давление выход, МПа"], input_values["Температура выход, ℃"], gas_composition)
            q,T = Calculate_file.heat_balance(input_values["Давление вход, МПа"],
                               input_values["Давление выход, МПа"],
                               input_values["Температура вход, ℃"],
                               input_values["Температура выход, ℃"],
                               input_values["Мощность котельной, кВт"],
                               Di_in,
                               Ccp_out,self.heat_balance_text)
                               
        except ValueError:
             self.heat_balance_text.insert(tk.END, "Ошибка: Введите числовые значения.")

        # self.heat_balance_text.insert(tk.END, f"Входное давление = {input_values["Давление вход, МПа"]}\n")
        # self.heat_balance_text.insert(tk.END, f"Выходное давление = {input_values["Давление выход, МПа"]}\n")
        # self.heat_balance_text.insert(tk.END, f"Расход = {q}\n")
        # self.heat_balance_text.insert(tk.END, f"Температура после теплообменника = {T}\n")
        
        self.heat_balance_text.config(state="disabled")

class Max_performance:
    def __init__(self,data_model,save_result):
        self.data_model = data_model
        self.save_result = save_result

    def get_data(self):# берем остольные данные из class Data Model
        self.input_pressure_range = self.data_model.get_input_pressure_range() #Диапазон входного давления
        self.output_pressure_range = self.data_model.get_output_pressure_range() #Диапазон выходного давления
        self.tables_data  = self.data_model.get_tables_data() # Названия таблиц

    def calculate_tube(self,col_pressure, data, df, col_name,table_name):
        
        self.calculate_propertys_gaz(col_pressure, data["gas_temperature_c"])
        df.at[table_name, col_name] = float(Calculate_file.calc(
            data["pipe_diameter"],  # Диаметр трубы
            data["wall_thickness"],  # Толщина стенки
            col_pressure,  # Давление на входе
            data["gas_temperature_c"],  # Температура газа
            data["gas_speed"],  # Скорость газа
            data["lines_count"],  # Количество линий
            self.z
        ))
        
    def calculate_regulator(self,col_pressure, p_out, data, df, col_name,table_name):
    
        self.calculate_propertys_gaz(col_pressure, float(self.data_model.get_temperature()["in"]))
        df.at[table_name, col_name] = float(Calculate_file.calculate_Ky(
            col_pressure,
            p_out,
            float(self.data_model.get_temperature()["in"]),
            self.Di,
            data["kv"],  
            data["lines_count"]  
        ))
        
    def calculate_heat_balance(self,col_pressure, p_out, data, df, col_name,table_name):
        
        self.calculate_propertys_gaz(col_pressure,float(self.data_model.get_temperature()["in"])) #получаем свойства газа
        df.at[table_name, col_name] = Calculate_file.heat_balance(
            col_pressure,  # Давление на входе
            p_out,             # Давление на выходе
            float(self.data_model.get_temperature()["in"]),
            float(self.data_model.get_temperature()["out"]),
            data["boiler_power"],           # Мощность котла
            self.Di,
            self.Ccp,
            True
        )

    def calculate_propertys_gaz(self,gas_pressure_mpa,gas_temperature_c):
        gas_composition = self.data_model.get_gas_composition()  # Получаем состав газа
        rho_rab, self.z, plotnost,self.Di,self.Ccp = Calculate_file.data_frame(gas_pressure_mpa, gas_temperature_c, gas_composition)
   
    def full_calculate(self,P_out:float)-> pd.DataFrame:
        self.get_data()
        print(self.input_pressure_range)
        df = pd.DataFrame()

        for table_name,table_type in self.tables_data.items():

            input_pressures = [float(p) for p in self.input_pressure_range]
            data = self.data_model.get_data_table(table_name)
            logger.info(f"Данные таблицы {data = }")
            
            for col_pressure in input_pressures:
                col_name = f"Pin_{str(col_pressure).replace('.', '_')}"
                
                match table_type:

                    case "Таблица для регуляторов":
                         self.calculate_regulator(col_pressure, P_out, data, df, col_name,table_name)
                        
                    case "Таблицы для труб до регулятора":
                        self.calculate_tube(col_pressure, data, df, col_name,table_name)
                    
                    case "Таблицы для труб после регулятора":
                        self.calculate_tube(P_out, data, df, col_name,table_name)

                    case "Таблица котельной":
                        self.calculate_heat_balance(col_pressure, P_out, data, df, col_name,table_name)
    
        logger.info(f"DataFrame для {P_out=} = получен")
        df_min = pd.DataFrame([df.min()])
        logger.info(f"Минимальный DataFrame  для {P_out=} отправлен на дальнейшую обработку")            
        self.save_result.save(df,f"Промежуточный результат  {P_out=}")
        logger.info(f"Сохранен промежуточный результат для {P_out=}")
        return df_min

class Result:
    def __init__(self,data_model,max_performance,save_result):
        self.data_model = data_model
        self.max_performance = max_performance
        self.save_result = save_result
    
    def get_data(self):
        self.output_pressure = self.data_model.get_output_pressure_range()

    def result_table(self):

        df_result = pd.DataFrame()
        self.get_data()
        for out_pressure in self.output_pressure:
            df_min = self.max_performance.full_calculate(out_pressure)
            # Устанавливаем индекс = текущее out_pressure для всех строк df_min
            df_min.index = [out_pressure] * len(df_min)

            df_result = pd.concat([df_result, df_min])
        self.save_result.save(df_result,"Результирующая таблица")
        logger.info(f"Сохранена результирующая таблица \n {df_result = }")

        plt.figure(figsize=(10, 6))

        input = [i.replace("Pin_","") for i in df_result.columns.tolist()]
        output = df_result.index.tolist()
        for output_pressure in output:
            plt.plot(
                input, 
                df_result.loc[output_pressure], 
                label=f"Выходное давление {output_pressure}"
            )
        # Настройка графика
        plt.title("График зависимости расхода от входного давления")
        plt.xlabel("Входное давление (МПа)")
        plt.ylabel("Расход")
        plt.legend(title="Выходное давление")
        plt.grid(True)
        # Отображение графика
        plt.show()

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

def create_log_file():
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)  # Создаем директорию, если её нет
    # Получаем текущую дату и время
    current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")  # Формат: ГГГГММДД_ЧЧММСС
    filename = os.path.join(log_dir, f"app_log_{current_time}.log")
    
    # Создаем файл (если он не существует)
    try:
        with open(filename, "x",encoding="utf-8") as f:  # Режим 'x' создает файл, если его нет
            f.write(f"Программа запущена: {current_time}\n")
        print(f"Файл '{filename}' создан.")
    except FileExistsError:
        print(f"Файл '{filename}' уже существует.")
    except Exception as e:
        print(f"Ошибка создания файла: {e}")
    return filename

if __name__ == "__main__":
    
    # Настройка логгера
    filename =create_log_file() 
    logger = logger_config.setup_logger(filename)
    
    save_result = Save_intermediate_result()
    root = tk.Tk()
    data_model = Data_model()
    fulCalc = Max_performance(data_model,save_result)
    result =Result(data_model,fulCalc,save_result)
    app = GuiManager(root, data_model,fulCalc,result)
    root.mainloop()
    