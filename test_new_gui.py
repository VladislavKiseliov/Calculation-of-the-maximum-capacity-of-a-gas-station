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
        self.controller =controller(self.gas_composition_manager,model)
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

class controller:
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
    
    

    root.mainloop()