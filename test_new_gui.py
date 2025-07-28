import contextlib
import logging
import math
import tkinter as tk
from tkinter import FALSE, Menu, messagebox, ttk
from typing import Dict, List

import logger_config
from DataModel import CSVManager, Data_model, DataBaseManager, DataStorage, JsonManager
from Work_table import BaseTableManager, TableFactory
from calculate_Max_performance import Max_performance 



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
            function=lambda: self.callback.trigger("create_window_temperature")
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
            self.parent, label_text="Автоматический расчет", row=6,function=lambda: self.callback.trigger("Расчет")
        )
        # self.calculate_button.config(state="disabled")

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
        self.temp_window = tk.Toplevel(self.parent)
        self.temp_window.attributes("-topmost", True)
        self.temp_window.title("Температурный режим")

        for idx, (title, label_text) in enumerate(
            [("input", "Температура на входе"), ("output", "Температура на выходе")]
        ):
            WidgetFactory.create_label(
                parent=self.temp_window, label_text=label_text, row=idx
            )
            entry = WidgetFactory.create_entry(parent=self.temp_window, row=idx)
            self.temperature_entries[title] = entry  # Сохраняем Entry по имен

        save_temperature_button = WidgetFactory.create_Button(
            parent=self.temp_window,
            label_text="Сохранить", row=3,
            function=lambda: self.callback.trigger("save_temperature")
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
            function=lambda: self.callback.trigger("save_pressure_range")
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
        self.add_table_button = WidgetFactory.create_Button(
            parent=self.table_window,
            label_text="Добавить таблицу",
            row=2,
            function=self.add_table
            
        )
    
    def add_table(self):
        self.selection = self.combobox.get()
        if not self.selection:
            logger.error("Тип таблицы не выбран")
            print("Ошибка: Таблица не выбрана!")
            return
        self.row += 1
        self.creating_fields(self.selection)

    def creating_fields(self,table_type,table_name = None):
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
        self.table_window,
        "Открыть таблицу",
        self.row,
        lambda e=self.entry_name_table: self.callback.trigger(
            "open_table", 
            name=e.get(), 
            table_type=table_type
        ),
        3
    )
        self.row += 1 

    def open_table_window(self, table_name,data = None):
        self.table_name = table_name
        """Открывает окно с таблицей."""
        logger.info(f"Открытие окна таблицы '{self.table_name}'")
        colomn = list(data.keys())
        col_values = list(data.values())
        init_data = col_values if data is not None else ["-"] * len(colomn)
        print(f"{data=}")
        
        try:
            window = tk.Toplevel(self.parent)
            window.title(f"Таблица: {self.table_name}")
            logger.debug(f"Создано новое окно для таблицы '{self.table_name}'")

            self.tree = ttk.Treeview(window, columns=colomn, show="headings")
            for col in colomn:
                self.tree.heading(col, text=col)
            self.tree.insert("", "end", values=init_data)
            # self.tree.pack(fill="both", expand=True)
            self.tree.grid(row=0, column=0, sticky="nsew")
            logger.debug("Treeview инициализирован с колонками")

            logger.debug("Данные загружены в Treeview")

            self.save_data_button = ttk.Button(window, text="Сохранить данные",command= lambda: self.callback.trigger("save_table"))

            
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

class TableController:

    def __init__(self, guitable: GuiTable, callback: CallbackRegistry, model : "Data_model"):
        self.logger = logging.getLogger("App.TableController")  # Дочерний логгер
        self.callback = callback
        self.guitable = guitable
        self.model = model
        self.tables = {}
        
    def create_window_table(self,tables: Dict[str,BaseTableManager]):
        print(f"{tables=}")
        if not tables:
            self.guitable.create_window_table()
        else:
            self.guitable.create_window_table()
            for name in tables:
                print(f"{tables=}")
                print(f"{tables[name]=}")
                print(f"{(tables[name])=}")
                self.guitable.creating_fields(tables[name].get_table_type(),name)


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
        data = {table_name:manager}
        self.model.save_table(data)
        self.model.create_db_table(table_name,self.tables[table_name].get_columns())
   
        
    def open_table(self,name, table_type):
        table_name = name
       
        if table_name not in self.tables:
            self.create_table(table_name, table_type)
                
        data = self.model.get_table_data(table_name)
        self.guitable.open_table_window(table_name, data)
 

    def save_table(self):
        data = self.get_table_data()
        [table_name] = data
        if table_name in self.tables:

            self.model.save_db_table(table_name,self.tables[table_name].get_columns(),data)


    def get_table_data(self) -> Dict[str, List[float]]:
        return self.guitable.get_data_table()

class Сontroller:
    def __init__(
        self, initial_data: Initial_data, model: "Data_model", callback: CallbackRegistry,table_controller:TableController,max_performance):
        self.logger = logging.getLogger("App.Сontroller")  # Дочерний логгер
        self.callback = callback
        self.initial_data = initial_data
        self.table_controller = table_controller
        self.model = model
        self.max_performance = max_performance
        self.logger.info("Контроллер работает")
        self._register_callback()

    def _register_callback(self):
        # Колбек на открытия меню входного и выходного давления
        self.callback.register(
            "save_gas_composition", self.gaz_window
        )  # "Сохранить состав газа"

        for pressure_type in ["input", "output"]:
            self.callback.register(
                f"{pressure_type}_pressure",
                lambda pt=pressure_type: self.setup_button_pressure(pt),
            )  

        self.callback.register(
            "save_gas_composition_to_csv",
            lambda: self.save_sostav_gaz(
                entries=self.initial_data.entries, to_csv=True
            ),
        )  # Колбек сохранения состава газа из csv

        self.callback.register(
            "load_gas_composition_to_csv", self.load_sostav_gaz_csv
        )  # Колбэк на загрузку данных из csv

        self.callback.register(
            "save_sostav_gaz", lambda: self.save_sostav_gaz(self.initial_data.entries)
        )  # сохранения состава газа в DataModel

        self.callback.register(
            "save_temperature",
            lambda: self.save_temperature(self.initial_data.temperature_entries),
        )

        self.callback.register("save_table",self.table_controller.save_table)
        self.callback.register("create_table_window", self.create_table)

        self.callback.register("save_temperature",lambda: self.save_temperature(self.initial_data.temperature_entries)
        )
        self.callback.register("create_window_temperature",self.create_window_temperature)

        self.callback.register("open_table",self.table_controller.open_table)
        
        self.callback.register("Расчет",self.max_performance.result)

    def setup_button_pressure(self, title):  # Функция для создание диапазона входных и выходных давлений

        self.initial_data.create_window_pressure(title)  # Создаем окно
        print(self.model.get_pressure_range(title))

        # Загрузка предыдущих значений
        if pressure_range := self.model.get_pressure_range(title):
            print(f"{pressure_range=}")
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
            self.model.save_gaz_to_csv(data)

        self.initial_data.gas_window.destroy() #Закрывает окно при успешном сохранении

    def load_sostav_gaz_csv(self):
        data = self.model.load_gaz_from_csv()
        print(f"{data=}")
        for component, entry in self.initial_data.entries.items():
            if component in data:
                entry.delete(0, tk.END)
                entry.insert(0, str(data[component]))
                self.initial_data.update_total_percentage()
    
    def create_window_temperature(self):
        self.initial_data.create_window_temperature()
        if temperature := self.model.get_temperature():

            self.initial_data.temperature_entries["input"].insert(
                0, temperature["input"]
            )
            self.initial_data.temperature_entries["output"].insert(
                0, temperature["output"]
            )

    def save_temperature(self, entries: Dict[str, tk.Entry]):
        data = {}
        for component in entries:
            data[component] = float(entries[component].get())
        
        self.model.save_temp(data)
        self.initial_data.temp_window.destroy()

    
    def create_table(self):
        tables = self.model.get_table_manager()
        self.table_controller.create_window_table(tables)

    

def test():
    print("бубубуб")
    root.after(500, test)

if __name__ == "__main__":
    filename = logger_config.create_log_file()
    logger = logger_config.setup_logger(filename)

    callback = CallbackRegistry()

    # Инициализируем объекты для работы с даннмы и файлами разных форматов 
    
    csvmanager = CSVManager()
    data_base_manager = DataBaseManager()
    json_manager = JsonManager()
    data_storage = DataStorage()
    model = Data_model(data_storage, csvmanager, data_base_manager,json_manager)
    
    root = tk.Tk()
    app = GuiManager(root)
    guitable = GuiTable(app.get_tab_frame(tab_name="Исходные данные"), callback)
    initial_data_manager = Initial_data( app.get_tab_frame(tab_name="Исходные данные"), callback)
    max_performance = Max_performance(model)

    table_controller = TableController(guitable, callback,model)
    controller = Сontroller(initial_data_manager, model, callback,table_controller,max_performance)
    # gas_properties_manager = Calculation_gas_properties(app.get_tab_frame())
    # tube_properties_manager = Calculation_pipi(app.get_tab_frame())
    # regulatormanager = Calculation_regulator(app.get_tab_frame())
    # heatbalancemanager = Heat_balance(app.get_tab_frame())
    # root.after(500, test)  #для запуска паралельной проверке для активации кнопки расчета
    
    root.mainloop()
