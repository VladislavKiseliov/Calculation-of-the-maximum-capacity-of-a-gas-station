


class Calculation_gas_properties:
    def __init__(self, parent):
        self.parent = parent["Свойства газа"]
        # self.data_model = data_model
        self.create_widgets()
        self.list = []

    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(
            parent=self.parent, label_text="Расчитать", row=2
        )

        label_pressure = WidgetFactory.create_label(self.parent, "Давление, МПа", 0, 0)
        label_temperature = WidgetFactory.create_label(
            self.parent, "Температура, ℃", 1, 0
        )
        self.entry_pressure = WidgetFactory.create_entry(self.parent, 0, 1)
        self.entry_temperature = WidgetFactory.create_entry(self.parent, 1, 1)

        self.gaz_text = tk.Text(self.parent, height=10, width=70, state="disabled")
        self.gaz_text.grid(row=0, column=3, rowspan=4, padx=10, pady=5, sticky="nsew")

    def start(self):
        try:
            p_in = float(self.entry_pressure.get())  # Получаем давление
            t_in = float(self.entry_temperature.get())  # Получаем температуру
        except ValueError:
            self.gaz_text.config(state="normal")
            self.gaz_text.delete("1.0", tk.END)
            self.gaz_text.insert(
                tk.END, "Ошибка: Введите числовые значения для давления и температуры."
            )
            self.gaz_text.config(state="disabled")
            return

        # gas_composition = self.data_model.data_gas_composition  # Получаем состав газа
        # rho_rab, z, plotnost,Di,Ccp = Calculate_file.data_frame(p_in, t_in, gas_composition)

        # self.data_model.set_gas_properties([rho_rab, z, plotnost,Di,Ccp])

        self.gaz_text.config(state="normal")
        self.gaz_text.delete("1.0", tk.END)
        self.gaz_text.insert(
            tk.END, f"=== Введенные данные ===\nДавление: {p_in}\nТемпература: {t_in}\n"
        )
        self.gaz_text.insert(
            tk.END, f"Плотность смеси при рабочих условиях: {rho_rab:.2f} кг/м3 \n"
        )
        self.gaz_text.insert(tk.END, f"Коэффициент сжимаемости: {z}\n")
        self.gaz_text.insert(
            tk.END, f"Плотность смеси при стандартных условиях: {plotnost:.4f} кг/м3 "
        )
        self.gaz_text.config(state="disabled")

class Calculation_regulator:
    def __init__(self, parent):
        self.parent = parent["Расчет регулятора"]
        # self.data_model = data_model
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать", 9)
        name_label = [
            "Давление вход, МПа",
            "Давление выход, МПа",
            "Температура, ℃",
            "Kv",
            "Количество линий",
        ]
        for i, name in enumerate(name_label):
            label = WidgetFactory.create_label(self.parent, name, i, 0)
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
            gas_composition = (
                self.data_model.data_gas_composition
            )  # Получаем состав газа
            rho_rab, z, plotnost, Di, Ccp = Calculate_file.data_frame(
                input_values["Давление вход, МПа"],
                input_values["Температура, ℃"],
                gas_composition,
            )
            q = Calculate_file.calculate_Ky(
                input_values["Давление вход, МПа"],
                input_values["Давление выход, МПа"],
                input_values["Температура, ℃"],
                plotnost,
                input_values["Kv"],
                input_values["Количество линий"],
            )

        except ValueError:
            self.regul_text.insert(tk.END, "Ошибка: Введите числовые значения.")

        self.regul_text.config(state="normal")
        self.regul_text.delete("1.0", tk.END)
        self.regul_text.insert(
            tk.END, f"Входное давление = {input_values['Давление вход, МПа']}\n"
        )
        self.regul_text.insert(
            tk.END, f"Выходное давление = {input_values['Давление выход, МПа']}\n"
        )
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
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать", 9)
        name_label = [
            "Давление вход, МПа",
            "Давление выход, МПа",
            "Температура вход, ℃",
            "Температура выход, ℃",
            "Мощность котельной, кВт",
        ]
        for i, name in enumerate(name_label):
            label = WidgetFactory.create_label(self.parent, name, i, 0)
            entry = WidgetFactory.create_entry(self.parent, i, 1)
            self.entries[name] = entry

        self.heat_balance_text = tk.Text(
            self.parent, height=10, width=50, state="disabled"
        )
        self.heat_balance_text.grid(
            row=0, column=3, rowspan=4, padx=10, pady=5, sticky="nsew"
        )

    def calc_heat_balance(self):
        try:
            input_values = {}
            self.heat_balance_text.config(state="normal")
            self.heat_balance_text.delete("1.0", tk.END)
            for name, entry in self.entries.items():
                value = float(entry.get())
                input_values[name] = value
            gas_composition = (
                self.data_model.data_gas_composition
            )  # Получаем состав газа
            rho_rab_in, z_in, plotnost_in, Di_in, Cc_in = Calculate_file.data_frame(
                input_values["Давление вход, МПа"],
                input_values["Температура вход, ℃"],
                gas_composition,
            )
            # rho_rab_out, z_out, plotnost_out,Di_out,Ccp_out = Calculate_file.data_frame(input_values["Давление выход, МПа"], input_values["Температура выход, ℃"], gas_composition)
            q, T = Calculate_file.heat_balance(
                input_values["Давление вход, МПа"],
                input_values["Давление выход, МПа"],
                input_values["Температура вход, ℃"],
                input_values["Температура выход, ℃"],
                input_values["Мощность котельной, кВт"],
                Di_in,
                Cc_in,
            )

        except ValueError:
            self.heat_balance_text.insert(tk.END, "Ошибка: Введите числовые значения.")

        self.heat_balance_text.insert(
            tk.END, f"Входное давление = {input_values['Давление вход, МПа']}\n"
        )
        self.heat_balance_text.insert(
            tk.END, f"Выходное давление = {input_values['Давление выход, МПа']}\n"
        )
        self.heat_balance_text.insert(tk.END, f"Расход = {q}\n")
        self.heat_balance_text.insert(
            tk.END, f"Температура после теплообменника = {T}\n"
        )
        self.heat_balance_text.insert(
            tk.END, f"Среднее значение коэффициента Джоуля-Томсона {Di_in}\n"
        )
        self.heat_balance_text.config(state="disabled")

class Calculation_pipi:
    def __init__(self, parent):
        self.parent = parent["Расчет пропускной способности трубы"]
        # self.data_model = data_model
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        # Кнопка для ввода свойств газа
        gas_button = WidgetFactory.create_Button(self.parent, "Расчитать", 0)

        # Список меток для полей ввода
        name_label = [
            "Давление, Мпа",
            "Температура, ℃",
            "Диаметр трубы, мм",
            "Толщина стенки трубы, мм",
            "Скорость газа в трубе, м/с",
            "Количество линий",
        ]
        # Создаем метки и поля ввода
        start_row = 1  # Начинаем с первой строки после кнопки
        for i, name in enumerate(name_label):
            label = WidgetFactory.create_label(self.parent, name, start_row + i, 0)
            entry = WidgetFactory.create_entry(self.parent, start_row + i, 1)
            self.entries[name] = entry

        # Текстовое поле для вывода результатов
        self.tube_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.tube_text.grid(
            row=start_row,
            column=3,
            rowspan=len(name_label),
            padx=10,
            pady=5,
            sticky="nsew",
        )

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
                input_values["Давление, Мпа"],
                input_values["Температура, ℃"],
                gas_composition,
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
