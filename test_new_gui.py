import math
import tkinter as ttk
import tkinter as tk
from tkinter import FALSE, Menu, ttk,filedialog
from wigets  import WidgetFactory
import Calculate_file
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
        self.entries = {}
        pass
    
    def create_wigets(self):
        self.gas_button = WidgetFactory.create_Button(self.parent,label_text="Ввести состав газа", row=1) 
        self.button_temp = WidgetFactory.create_Button(parent=self.parent,label_text="Температура газа",row=2)
        self.input_pressure = WidgetFactory.create_Button(parent=self.parent, label_text="Диапазон входных давлений",row=3)
        self.output_pressure = WidgetFactory.create_Button(parent=self.parent, label_text="Диапазон выходных давлений",row=4)
        self.input_table_button = WidgetFactory.create_Button(parent=self.parent,label_text="Исходные таблицы",row=5)
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
        # self.load_gas_composition()

        # Кнопка для сохранения данных
        self.save_gaz_sostav_button = WidgetFactory.create_Button(self.gas_window, "Сохранить", self.row_last_components)
        #Кнопка для сохранения в файл
        self.save_to_file_button = WidgetFactory.create_Button(parent=self.gas_window,label_text="Сохранить в файл",row = self.row_last_components+1)
         #Кнопка для открытия из файла
        self.load_from_file_button = WidgetFactory.create_Button(self.gas_window,"Открыть из файла",self.row_last_components+2)

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

class controller:
    def __init__(self,initial_data:Initial_data,model:'Model',data_model:'Data_model'):
        self.initial_data = initial_data
        self.model = model
        self.data_model = data_model
        self.setup_buttom()


    def setup_buttom(self):
        self.initial_data.gas_button.configure(command = self.work_sostav_gaz)
        self.initial_data.save_gaz_sostav_button.configure(command = self.work_sostav_gaz)


    def update_state_button(self):
        """
        Проверяем введены ли исходные данные для автоматического расчета
        """
        input_pressure = self.data_model.get_input_pressure_range()
        output_pressure = self.data_model.get_output_pressure_range()
        table = self.data_model.get_data_table()
        temp = self.data_model.get_temperature()
        if (input_pressure and output_pressure and table and temp["in"] and temp["out"] is None):
            pass
        pass

    def work_sostav_gaz(self):
        self.initial_data.create_window_sostav_gaz()
        print("Работает")



class Model:
    def __init__(self,calc_gaz):
        self.calc_gaz=calc_gaz
        pass

    def work_gas(self,entries):
        self.calc_gaz.update_total_percentage(entries)



class Calculate_gaz:
    def __init__(self):
        pass
    

    def load_gas_composition(self):

        """Loads the gas composition from the data model and updates the entry fields."""
        saved_composition = self.data_model.data_gas_composition
        for component, entry in self.entries.items():
            if component in saved_composition:
                entry.delete(0, tk.END)
                entry.insert(0, str(saved_composition[component]))
         # Обновляем сумму после загрузки данных
        self.update_total_percentage()


calc_gaz=Calculate_gaz()
model = Model(calc_gaz)






























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
    
 
    root = tk.Tk()
    app = GuiManager(root)
    
    root.mainloop()