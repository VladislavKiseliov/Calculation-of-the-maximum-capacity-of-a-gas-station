import contextlib
import logging
import math
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import FALSE, Menu, messagebox, ttk
from tkinter.messagebox import showwarning
from typing import Dict, List

import numpy as np

import Calculate_file
import logger_config
from DataModel import CSVManager, Data_model, DataBaseManager
from wigets import WidgetFactory
from Tab_calculate import Calculation_gas_properties,Calculation_regulator,Heat_balance,Calculation_pipi

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
    def create_Button(parent, label_text, row, function=None, column=0, padx=5, pady=5):
        Button = ttk.Button(parent, text=label_text, command=function)
        Button.grid(row=row, column=column, padx=padx, pady=pady, sticky="ew")
        return Button


class CallbackRegistry:
    def __init__(self):
        self.callbacks = {}

    def register(self, event_name: str, callback):
        """Регистрация колбэка для события."""
        self.callbacks[event_name] = callback

    def trigger(self, event_name, *args, **kwargs):
        """Вызов колбэка для события."""
        if event_name in self.callbacks:
            self.callbacks[event_name](*args, **kwargs)
        else:
            print(f"Колбэк для события '{event_name}' не зарегистрирован")


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
        self.root.minsize(700, 300)  # Минимальный размер окна

    def get_tab_frame(self, tab_name: str) -> Dict[str, tk.Frame]:
        return self.tabs[tab_name]

    def _create_menu(self):
        self.root.option_add("*tearOff", FALSE)

        main_menu = Menu()

        file_menu = Menu()
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Open")
        file_menu.add_separator()
        file_menu.add_command(label="Exit")

        main_menu.add_cascade(label="Файл", menu=file_menu)
        main_menu.add_cascade(label="Настройка")
        main_menu.add_cascade(label="Справка")
        self.root.config(menu=main_menu)

    def _create_style(self):
        # Настраиваем стили
        # Убираем пунктирную рамку вокруг активной вкладки
        # Полностью убираем рамки и выделение для вкладок
        self.style.configure(
            "TNotebook.Tab",
            background="#e0e0e0",  # Цвет фона вкладки
            padding=[10, 5],  # Отступы внутри вкладки
            font=("Arial", 10, "bold"),
            borderwidth=0,  # Нет границ
            highlightthickness=0,  # Нет выделения
        )

        # Для активной вкладки (убираем рамку при выборе)
        self.style.map(
            "TNotebook.Tab",
            background=[("selected", "#d0d0d0")],
            expand=[("selected", [0, 0, 0, 0])],  # Убираем расширение рамки
        )
        self.style.theme_use("clam")  # Современная тема
        self.style.configure("TFrame", background="#f0f0f0")
        self.style.configure("TLabel", font=("Arial", 10), background="#f0f0f0")
        self.style.configure(
            "TButton", font=("Arial", 10, "bold"), padding=5, background="#4CAF50"
        )
        self.style.configure("Treeview", rowheight=25, font=("Arial", 10))

    def _create_notebook(self):
        # Создаем Notebook с стилем
        self.notebook = ttk.Notebook(root, style="Custom.TNotebook")
        self.style.configure("Custom.TNotebook", tabposition="n", background="#e0e0e0")
        # self.notebook.pack(fill="both", expand=True)
        self.notebook.grid(row=0, column=0, sticky="nsew")

        # Создаем ссписок для названий вкладок расчетов
        tabs_name = [
            "Исходные данные",
            "Свойства газа",
            "Расчет пропускной способности трубы",
            "Расчет регулятора",
            "Тепловой баланс",
        ]

        for name in tabs_name:
            frame = ttk.Frame(self.notebook)
            self.tabs[name] = frame  # Сохраняем фрейм в словаре
            self.notebook.add(frame, text=name)


class Initial_data:

    def __init__(self, parent, callback: CallbackRegistry):
        self.callback = callback
        self.parent = parent
        self.create_wigets()
        self.entries = {}  # Словарь хранения данных
        self.callbacks = {}  # Хранилище для колбэков

    
    def create_wigets(self):
        self.gas_button = WidgetFactory.create_Button(
            self.parent,
            label_text="Ввести состав газа",
            row=1,
            function=lambda: self.callback.trigger("save_gas_composition"),
        )
        self.button_temp = WidgetFactory.create_Button(
            parent=self.parent,
            label_text="Температура газа",
            row=2,
            function=self.create_window_temperature,
        )
        self.input_pressure = WidgetFactory.create_Button(
            parent=self.parent,
            label_text="Диапазон входных давлений",
            row=3,
            function=lambda: self.callback.trigger("input_pressure"),
        )
        self.output_pressure = WidgetFactory.create_Button(
            parent=self.parent,
            label_text="Диапазон выходных давлений",
            row=4,
            function=lambda: self.callback.trigger("output_pressure"),
        )
        self.input_table_button = WidgetFactory.create_Button(
            parent=self.parent,
            label_text="Исходные таблицы",
            row=5,
            function=lambda: self.callback.trigger(
                "create_table_window",
            ),
        )
        self.calculate_button = WidgetFactory.create_Button(
            self.parent, label_text="Автоматический расчет", row=6
        )
        self.calculate_button.config(state="disabled")

    def create_window_sostav_gaz(self, data: Dict[str, float]):
        # Окно для ввода состава газа
        self.gas_window = tk.Toplevel(self.parent)
        self.gas_window.title("Состав газа")

        # Список компонентов с формулами
        self.components = [
            "Метан: CH4",
            "Этан: C2H6",
            "Пропан: C3H8",
            "н-Бутан: n-C4H10",
            "и-Бутан: i-C4H10",
            "н-Пентан: n-C5H12",
            "и-Пентан: i-C5H12",
            "н-Гексан: n-C6H14",
            "н-Гептан: n-C7H16",
            "н-Октан: n-C8H18",
            "Ацетилен: C2H2",
            "Этилен: C2H4",
            "Пропилен: C3H6",
            "Бензол: C6H6",
            "Толуол: C7H8",
            "Водород: H2",
            "Водяной пар: H2O",
            "Аммиак: NH3",
            "Метанол: CH3OH",
            "Сероводород: H2S",
            "Метилмеркаптан: CH3SH",
            "Диоксид серы: SO2",
            "Гелий: He",
            "Неон: Ne",
            "Аргон: Ar",
            "Моноксид углерода: CO",
            "Азот: N2",
            "Воздух",
            "Кислород: O2",
            "Диоксид углерода: CO2",
        ]
        # Создаем метки и поля ввода для каждого компонента

        mediana = int((len(self.components) / 2.0)) - 1

        for i, component in enumerate(self.components):
            if i <= mediana:
                label = WidgetFactory.create_label(self.gas_window, component, i, 0)
                enty = WidgetFactory.create_entry(self.gas_window, i, 1)
            else:
                label = WidgetFactory.create_label(
                    self.gas_window, component, i - 15, 3
                )
                enty = WidgetFactory.create_entry(self.gas_window, i - 15, 4)

            if component in data:
                enty.delete(0, tk.END)
                enty.insert(0, str(data[component]))

            enty.bind("<KeyRelease>", self.update_total_percentage)
            self.entries[component] = enty

        self.total_label = WidgetFactory.create_label(
            parent=self.gas_window,
            label_text="Сумма: 0.0%",
            row=math.floor((len(self.components) / 2)),
            column=4,
        )
        # Load previously saved composition, if available
        self.update_total_percentage()
        self.row_last_components = math.ceil((len(self.components) / 2) + 1)

        # Кнопка для сохранения данных
        self.save_gaz_sostav_button = WidgetFactory.create_Button(
            self.gas_window,
            "Сохранить",
            self.row_last_components,
            function=lambda: self.callback.trigger("save_sostav_gaz"),
        )
        # Кнопка для сохранения в файл
        self.save_to_file_button = WidgetFactory.create_Button(
            parent=self.gas_window,
            label_text="Сохранить в файл",
            row=self.row_last_components + 1,
            function=lambda: self.callback.trigger("save_gas_composition_to_csv"),
        )
        # Кнопка для открытия из файла
        self.load_from_file_button = WidgetFactory.create_Button(
            self.gas_window,
            "Открыть из файла",
            self.row_last_components + 2,
            function=lambda: self.callback.trigger("load_gas_composition_to_csv"),
        )

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
        # data: Dict[str, float]
        self.temperature_entries = {}
        pressure_window = tk.Toplevel(self.parent)
        pressure_window.attributes("-topmost", True)
        pressure_window.title("Температурный режим")

        for idx, (title, label_text) in enumerate(
            [("input", "Температура на входе"), ("output", "Температура на выходе")]
        ):
            WidgetFactory.create_label(
                parent=pressure_window, label_text=label_text, row=idx
            )
            entry = WidgetFactory.create_entry(parent=pressure_window, row=idx)
            self.temperature_entries[title] = entry  # Сохраняем Entry по имени

        # # temperature = self.data_model.get_temperature()
        # print(f"{temperature=}")
        # if temperature:
        #     # min_pressure_entry.insert(0, min(pressure_range))

        #     self.entries_dict["input"].insert(0,temperature['in'])
        #     self.entries_dict["output"].insert(0,temperature['out'])

        self.save_button = WidgetFactory.create_Button(
            pressure_window, label_text="Сохранить", row=3
        )

    def create_window_pressure(self, title):
        """
        Открывает диалоговое окно для ввода диапазона давлений.
        """
        self.title = title
        self.pressure_window = tk.Toplevel(self.parent)
        self.pressure_window.title(self.title)

        labels = ["Минимальное давление:", "Максимальное давление:", "Шаг значения"]
        self.pressure_entries = {}

        for i, label_text in enumerate(labels):
            ttk.Label(self.pressure_window, text=label_text).grid(
                row=i, column=0, padx=5, pady=5
            )
            entry = WidgetFactory.create_entry(self.pressure_window, row=i, column=1)
            self.pressure_entries[labels[i]] = entry

        self.save_button = WidgetFactory.create_Button(
            parent=self.pressure_window,
            label_text="Сохранить",
            row=4,
            function=lambda: self.callback.trigger("save_pressure_range"),
        )
        


class GuiTable:
    
    def __init__(self, parent,callback):
        self.parent = parent
        self.callback = callback
        self.row = 3
        self.tables = {}  # Хранит все таблицы: {"table_name": manager}
        self.table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной",
            "Таблицы для труб до регулятора",
            "Таблицы для труб после регулятора",
        ]
        
    def create_window_table(self):
       
        self.table_window = tk.Toplevel(self.parent)
        self.table_window.title("Таблицы граничных условий")

        # Метка для выбора таблицы
        label = WidgetFactory.create_label(self.table_window, "Выберите таблицу:", 0)

        # Combobox
        self.combobox = ttk.Combobox(
            self.table_window, values=self.table_labels, state="readonly", width=33
        )
        self.combobox.grid(row=1, column=0, padx=5, pady=5)

        # Кнопка добавления таблицы
        self.save_button = WidgetFactory.create_Button(
            parent=self.table_window,
            label_text="Добавить таблицу",
            row=2,
        )
    
    def check_table(self):
        if len(self.tables) == 0:
            self.create_window_table()
        else:
            self.create_window_table()
            for name in self.tables:
                self._creating_fields(name,self.table_labels[name].get_table_type())

                self.row += 1

    def add_table(self):
        self.selection = self.combobox.get()
        if not self.selection:
            logger.error("Тип таблицы не выбран")
            print("Ошибка: Таблица не выбрана!")
            return
        self.row += 1
        self._creating_fields(self.selection)

    def _creating_fields(self,table_type,table_name = None):
        # Метка с названием таблицы
        type_label = WidgetFactory.create_label(
            self.table_window, label_text=table_type, row=self.row
        )
        # Поле ввода имени таблицы
        self.entry_name_table = WidgetFactory.create_entry(
            self.table_window, self.row, 1
        )
        if table_name:
            self.entry_name_table.insert(0, table_name)

        # Кнопка для открытия таблицы
        self.open_button = WidgetFactory.create_Button(
            self.table_window, "Открыть таблицу", self.row, None, 3
        )

    def open_table_window(self, table_name, colomn):
        self.table_name = table_name
        """Открывает окно с таблицей."""
        logger.info(f"Открытие окна таблицы '{self.table_name}'")
        try:
            window = tk.Toplevel(self.parent)
            window.title(f"Таблица: {self.table_name}")
            logger.debug(f"Создано новое окно для таблицы '{self.table_name}'")

            self.tree = ttk.Treeview(window, columns=colomn, show="headings")
            for col in colomn:
                self.tree.heading(col, text=col)
                self.tree.insert("", "end", values=["1", "2"])
            # self.tree.pack(fill="both", expand=True)
            self.tree.grid(row=0, column=0, sticky="nsew")
            logger.debug("Treeview инициализирован с колонками")

            logger.debug("Данные загружены в Treeview")

            self.save_data_button = ttk.Button(window, text="Сохранить данные",command= lambda: self.callback.trigger("save_table"))

            # self.save_button.pack(pady=10)
            # Замените pack на grid для кнопки
            self.save_data_button.grid(row=1, column=0, pady=10, sticky="ew")
            logger.debug("Кнопка сохранения добавлена в окно")

            self.tree.bind("<Double-1>", self._add_editing_features)
            logger.debug("Событие двойного клика привязано к редактированию ячеек")

        except Exception as e:
            logger.exception(f"Ошибка при открытии окна таблицы '{self.table_name}'")
            messagebox.showerror("Ошибка", f"Не удалось открыть таблицу: {e}")

    def _add_editing_features(self, event):
        """Обработка двойного клика для редактирования ячейки."""
        # Получаем выбранную строку и столбец
        print(123)
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

    def get_data_table(self) -> Dict[str, List[float]]:
        print([self.tree.item(item)["values"] for item in self.tree.get_children()][0])
        return {
            self.table_name: [
                self.tree.item(item)["values"] for item in self.tree.get_children()
            ][0]
        }

class BaseTableManager(ABC):
    def __init__(self, table_type):
        self.table_type = table_type

    @abstractmethod
    def get_columns(self) -> list:
        pass

    def get_table_type(self) -> str:
        return self.table_type

class RegulatorTableManager(BaseTableManager):
    def get_columns(self):
        return ["regulator", "kv", "lines_count"]

class BoilerTableManager(BaseTableManager):
    def get_columns(self):
        return ["boiler_power", "gas_temp_in", "gas_temp_out"]

class PipeTableManager(BaseTableManager):
    def get_columns(self):
        return [
            "pipe_diameter",
            "wall_thickness",
            "gas_speed",
            "gas_temperature",
            "lines_count",
        ]

class TableFactory:
    @staticmethod
    def create_table_manager(table_type):
        logger = logging.getLogger("App.TableFactory")  # Дочерний логгер
        logger.info(f"Запрос на создание менеджера таблицы типа: '{table_type}'")

        match table_type:
            case "Таблица для регуляторов":
                logger.info("Создан менеджер таблицы регуляторов")
                return RegulatorTableManager(table_type)

            case "Таблица котельной":
                logger.info("Создан менеджер таблицы котельной")
                return BoilerTableManager(table_type)

            case "Таблицы для труб до регулятора" | "Таблицы для труб после регулятора":
                logger.info(f"Создан менеджер таблицы труб: {table_type}")
                return PipeTableManager(table_type)

            case _:
                error_msg = f"Неизвестный тип таблицы: {table_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)


class TableController:

    def __init__(self, guitable: GuiTable, callback: CallbackRegistry):
        self.logger = logging.getLogger("App.TableController")  # Дочерний логгер
        self.callback = callback
        self.guitable = guitable
        self.tables = {}

        self.callback.register("create_table_window", self.create_window_table)

    def create_window_table(self):
        self.guitable.check_table()
        self.guitable.save_button.configure(command=self._add_table)

    def _add_table(self):
        self.guitable.add_table()
        # print(f"{self.guitable.entry_name_table.get()=}")
        self.guitable.open_button.configure(
            command=lambda e=self.guitable.entry_name_table, s=self.guitable.selection: self.open_table(e.get(), s)
        )

    def create_table(self, table_name, table_type):
        if table_name == "":
            messagebox.showwarning("Ошибка", "Введите название таблицы")
            return

        if table_name in self.tables:
            logger.warning(f"Таблица '{table_name}' уже существует")
            messagebox.showwarning("Ошибка", f"Таблица '{table_name}' уже существует!")
            return
        manager = TableFactory.create_table_manager(table_type)
        self.tables[table_name] = manager

    def open_table(self, table_name, table_type):
        if table_name not in self.tables:
            self.create_table(table_name, table_type)
        self.guitable.open_table_window(
            table_name, self.tables[table_name].get_columns()
        )
    
    def get_table_data(self) -> Dict[str, List[float]]:
        return self.guitable.get_data_table()


class Сontroller:
    def __init__(
        self, initial_data: Initial_data, model: "Model", callback: CallbackRegistry,table_controller):
        self.logger = logging.getLogger("App.Сontroller")  # Дочерний логгер
        self.callback = callback
        self.initial_data = initial_data
        self.table_controller = table_controller
        self.model = model
        self.logger.info("Контроллер работает")
        self._register_callback()

    def _register_callback(self):
        self.callback.register(
            "save_gas_composition", self.gaz_window
        )  # "Сохранить состав газа"

        for pressure_type in ["input", "output"]:
            self.callback.register(
                f"{pressure_type}_pressure",
                lambda pt=pressure_type: self.setup_button_pressure(pt),
            )  # Колбек на открытия меню входного и выходного давления

        self.callback.register(
            "save_gas_composition_to_csv",
            lambda: self.save_sostav_gaz(
                entries=self.initial_data.entries, to_csv=True
            ),
        )  # Колбек сохранения состава газа из csv

        self.callback.register(
            "load_gas_composition_to_csv", self.model.load_gaz_from_csv
        )  # Колбэк на загрузку данных из csv

        self.callback.register(
            "save_sostav_gaz", lambda: self.save_sostav_gaz(self.initial_data.entries)
        )  # сохранения состава газа в DataModel

        self.callback.register(
            "save_temperature",
            lambda: self.save_temperature(self.initial_data.temperature_entries),
        )

        self.callback.register("save_table",self.save_table)
        
    def setup_button_pressure(self, title):  # Функция для создание диапазона входных и выходных давлений
        self.initial_data.create_window_pressure(title)  # Создаем окно
        # # Загрузка предыдущих значений
        if pressure_range := getattr(
            self.model.data_model, f"get_{title.lower()}_pressure_range"
        )():
            self.initial_data.pressure_entries["Минимальное давление:"].insert(
                0, min(pressure_range)
            )
            self.initial_data.pressure_entries["Максимальное давление:"].insert(
                0, max(pressure_range)
            )
            self.initial_data.pressure_entries["Шаг значения"].insert(
                0, pressure_range[1] - pressure_range[0]
            )

        self.callback.register(
            "save_pressure_range",self.save_pressure)  # Привязываю функцию для сохранение диапазона давлениея

    def save_pressure(self):
        self.model.save_pressure_range1(
            self.initial_data.title,  # Передаем title
                self.initial_data.pressure_entries,  # Передаем поля для ввода
            )
        self.initial_data.pressure_window.destroy() #Закрывает окно при успешном сохранении

    def gaz_window(self):
        """
        Create window for gas composition
        """
        data = self.model.load_gas_composition()
        self.initial_data.create_window_sostav_gaz(data)

    def save_sostav_gaz(self, entries: Dict[str, tk.Entry], to_csv=False):
        """
        Saving the gas composition in csv format and/or in storage
        """
        data = {component: entries[component].get() for component in entries}
        model.save_sostav_gaz(data)

        if to_csv:  # Для сохранения в csv
            self.model.save_gaz_to_csv()

        self.initial_data.gas_window.destroy() #Закрывает окно при успешном сохранении

    def save_temperature(self, entries: Dict[str, tk.Entry]):
        data = {}

        for component in entries:
            data[component] = entries[component].get()
            print(f"{entries[component].get()=}")

    def save_table(self):
        data = self.table_controller.get_table_data()
        print(f"{data=}")
        self.model.data_table(data)

class Model:
    def __init__(
        self, data_model: Data_model, csvmanager: CSVManager, data_base: DataBaseManager
    ):
        self.data_model = data_model
        self.data_base_manager = data_base

    def _calculate_pressure_range(
        self, min_pressure, max_pressure, average_value
    ) -> List[float]:
        try:
            # Проверка корректности данных
            if min_pressure > max_pressure:
                raise ValueError("Ошибка: Минимальное давление больше максимального.")
            if average_value <= 0:
                raise ValueError("Ошибка: Шаг должен быть положительным числом.")

            pressure_range = np.arange(
                min_pressure, max_pressure + average_value, average_value
            ).tolist()
            return [round(p, 1) for p in pressure_range]

        except ValueError as e:
            # Вывод ошибки
            showwarning("Ошибка", e)
            return

    def save_pressure_range1(self, title: str, pressure_entries: Dict[str, ttk.Entry]):
        """
        Сохраняет диапазон давлений.
        """
        # Преобразуем входные данные в числа
        min_pressure = float(pressure_entries["Минимальное давление:"].get())
        max_pressure = float(pressure_entries["Максимальное давление:"].get())
        avg_value = float(pressure_entries["Шаг значения"].get())

        if not all([min_pressure, max_pressure, avg_value]):
            raise ValueError("Ошибка: Введите значения")

        try:
            pressure_type = title.lower()
            set_pressure_range = self._calculate_pressure_range(
                min_pressure, max_pressure, avg_value
            )

            print(f"{set_pressure_range=}")
            self.data_model.set_pressure_range(pressure_type, set_pressure_range)

            logger.info(
                f"Диапазоны {pressure_type} давления  успешно сохранены: максимальное = %s мПа, минимальное = %s мПа,шаг = %s",
                max_pressure,
                min_pressure,
                avg_value,
            )
        except ValueError:
            logger.warning("Введите корректные числовые значения!")
            showwarning("Ошибка", "Введите корректные числовые значения!")

    def load_gas_composition(self):
        """Loads the gas composition from the data model and updates the entry fields."""
        return self.data_model.data_gas_composition

    def save_sostav_gaz(self, data):
        self.data_model.data_gas_composition = data

    def save_gaz_to_csv(self):  # Исправить на класс работы с csv
        self.data_model.save_gas_composition_to_csv()

    def load_gaz_from_csv(self):  # Исправить на класс работы с csv
        self.data_model.load_gas_composition_from_csv()

    def data_table(self, data):
        # Проверяем, что словарь не пуст
        if not data:
            print("Словарь пуст!")
            return
        # Получаем ключ и список из словаря
        key, data1 = next(
            iter(data.items())
        )  # Берем первую (и единственную) пару ключ-значение
        self.data_base_manager.create_table(key, ["1", "2"])
        # self.data_base_manager.save_data(data1, key, ["1", "2"])




if __name__ == "__main__":
    filename = logger_config.create_log_file()
    logger = logger_config.setup_logger(filename)

    callback = CallbackRegistry()
    data_model = Data_model()
    csvmanager = CSVManager()
    
    root = tk.Tk()
    app = GuiManager(root)


    guitable = GuiTable(app.get_tab_frame(tab_name="Исходные данные"), callback)
    initial_data_manager = Initial_data( app.get_tab_frame(tab_name="Исходные данные"), callback)
    
    data_base_manager = DataBaseManager()
    
    model = Model(data_model, csvmanager, data_base_manager)

    
    table_controller = TableController(guitable, callback)
   
    controller = Сontroller(initial_data_manager, model, callback,table_controller)
   
    # gas_properties_manager = Calculation_gas_properties(app.get_tab_frame())
    # tube_properties_manager = Calculation_pipi(app.get_tab_frame())
    # regulatormanager = Calculation_regulator(app.get_tab_frame())
    # heatbalancemanager = Heat_balance(app.get_tab_frame())

    
    

    root.mainloop()
