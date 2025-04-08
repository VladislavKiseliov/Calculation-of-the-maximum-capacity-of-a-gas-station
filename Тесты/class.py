import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showwarning, showinfo
import numpy as np


class GUI:
    def __init__(self, root, calculator):
        self.root = root
        self.calculator = calculator  # Ссылка на объект Calculate
        self.root.title("Меню ввода исходных данных")

        # Инициализация переменных для хранения данных
        self.gas_composition = None
        self.input_pressure_range = None
        self.output_pressure_range = None

        # Создание виджетов
        self.create_widgets()

    def create_widgets(self):
        # Заголовок
        title_label = ttk.Label(self.root, text="Меню ввода исходных данных", font=("Arial", 14, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Кнопка для ввода состава газа
        gas_button = ttk.Button(self.root, text="Ввести состав газа", command=self.input_gas_composition)
        gas_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Кнопка для ввода диапазона входных давлений
        input_pressure_button = ttk.Button(self.root, text="Указать диапазон входных давлений",
                                          command=lambda: self.input_pressure_range_dialog("Вход"))
        input_pressure_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Кнопка для ввода диапазона выходных давлений
        output_pressure_button = ttk.Button(self.root, text="Указать диапазон выходных давлений",
                                           command=lambda: self.input_pressure_range_dialog("Выход"))
        output_pressure_button.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Кнопка для ввода исходных таблиц
        input_table = ttk.Button(self.root, text="Исходные таблицы",
                                                command=self.create_input_table)
        input_table.grid(row=4, column=0, padx=10, pady=5, sticky="ew")

        # Кнопка для просмотра данных
        view_data_button = ttk.Button(self.root, text="Просмотреть введенные данные", command=self.view_data)
        view_data_button.grid(row=5, column=0, padx=10, pady=5, sticky="ew")

        # Текстовое поле для отображения данных
        self.data_text = tk.Text(self.root, height=10, width=50, state="disabled")
        self.data_text.grid(row=1, column=1, rowspan=4, padx=10, pady=5, sticky="nsew")
        
    def input_gas_composition(self):
        # Окно для ввода состава газа
        self.gas_window = tk.Toplevel(self.root)
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
            "Кислород: O2",
            "Диоксид углерода: CO2"
        ]

        # Создаем метки и поля ввода для каждого компонента
        self.entries = {}
        for i, component in enumerate(self.components):
            label = ttk.Label(self.gas_window, text=component)
            label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            entry = ttk.Entry(self.gas_window)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[component] = entry

        # Кнопка для сохранения данных
        save_button = ttk.Button(self.gas_window, text="Сохранить", command = self.save_gas_composition)
        save_button.grid(row=len(self.components), column=0, columnspan=2, pady=10)
        

    def save_gas_composition(self):
        # Сохраняем данные в классе Calculate
        self.calculator.save_gas_composition(self.entries)
        self.gas_window.destroy()

    def create_input_table(self):
        table_window = tk.Toplevel(self.root)
        table_window.title('Количество исходных таблиц')
        # Список с названиями таблиц
        table_labels = [
            "Таблица для регуляторов",
            "Таблица котельной",
            "Таблицы для труб"
        ]
        # Словарь для хранения полей ввода
        self.entries = {}
        # Создаем метки и поля ввода в цикле
        for i, label_text in enumerate(table_labels, start=1):
            label = ttk.Label(table_window, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=2, sticky="w")

            entry = ttk.Entry(table_window)
            entry.grid(row=i, column=1, padx=5, pady=2)
            self.entries[label_text] = entry
        # Кнопка для сохранения данных
        save_button = ttk.Button(table_window, text="Сгенерировать таблицы",command=self.save_count_table)
        save_button.grid(row=len(table_labels) + 1, column=0, columnspan=2, pady=10)
        
    def save_count_table(self):
        # Собираем данные из полей ввода
        table_data = {label: entry.get() for label, entry in self.entries.items()}
        
        # Выводим данные в консоль (или используем их для генерации таблиц)
        print("Данные для генерации таблиц:")
        for label, value in table_data.items():
            print(f"{label}: {value}")





    def input_pressure_range_dialog(self, title):
        # Окно для ввода диапазона давлений
        pressure_window = tk.Toplevel(self.root)
        pressure_window.title(title)

        ttk.Label(pressure_window, text="Минимальное давление:").grid(row=0, column=0, padx=5, pady=5)
        min_pressure_entry = ttk.Entry(pressure_window)
        min_pressure_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(pressure_window, text="Максимальное давление:").grid(row=1, column=0, padx=5, pady=5)
        max_pressure_entry = ttk.Entry(pressure_window)
        max_pressure_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(pressure_window, text="Шаг значения").grid(row=2, column=0, padx=5, pady=5)
        average_value_entry = ttk.Entry(pressure_window)
        average_value_entry.grid(row=2, column=1, padx=5, pady=5)
        status_label = ttk.Label(pressure_window, text="")
        status_label.grid(row=4, column=0, columnspan=2)

        save_button = ttk.Button(pressure_window, text="Сохранить",
                                command=lambda: self.save_pressure_range(title, min_pressure_entry.get(),
                                                                        max_pressure_entry.get(),
                                                                        average_value_entry.get(),status_label,pressure_window))
      
        save_button.grid(row=3, column=0, columnspan=2, pady=10)

        

    def save_pressure_range(self, title, min_pressure_entry,max_pressure_entry,average_value_entry ,status_label,pressure_window):
        try:
            if title == "Вход":
               self.input_pressure_range = self.calculator.save_pressure(min_pressure_entry,max_pressure_entry,average_value_entry,status_label)
            elif title == "Выход":
                self.output_pressure_range = self.calculator.save_pressure(min_pressure_entry,max_pressure_entry,average_value_entry,status_label)

            showinfo("Успех", "Данные успешно сохранены!")
            pressure_window.destroy()
        except ValueError:
            showwarning("Ошибка", "Введите корректные числовые значения!")

    def view_data(self):
        self.data_text.config(state="normal")
        self.data_text.delete("1.0", tk.END)

        self.data_text.insert(tk.END, "=== Введенные данные ===\n")
        if self.calculator.gas_composition:
            self.data_text.insert(tk.END, "Состав газа:\n")
            for component, percentage in self.calculator.gas_composition.items():
                if percentage!=0:
                    self.data_text.insert(tk.END, f"  {component}: {percentage}%\n")
        else:
            self.data_text.insert(tk.END, "Состав газа: Не указан\n")

        if self.input_pressure_range is not None:
            self.data_text.insert(tk.END, f"Диапазон входных давлений: {self.input_pressure_range}\n")
        else:
            self.data_text.insert(tk.END, "Диапазон входных давлений: Не указан\n")

        if self.output_pressure_range is not None:
            self.data_text.insert(tk.END, f"Диапазон выходных давлений: {self.output_pressure_range}\n")
        else:
            self.data_text.insert(tk.END, "Диапазон выходных давлений: Не указан\n")

        self.data_text.config(state="disabled")


class Calculate:
    def __init__(self):
        # Переменные для хранения данных
        self.gas_composition = {}
        self.input_pressure_range = None
        self.output_pressure_range = None

    def save_gas_composition(self,entries):
        # Сохраняем введенные данные
        self.gas_composition = {}
        total_percentage = 0.0
        for component, entry in entries.items():
            try:
                percentage = float(entry.get())
                if percentage < 0:
                    raise ValueError("Отрицательное значение")
                self.gas_composition[component] = percentage
                total_percentage += percentage
            except ValueError:
                self.gas_composition[component] = 0.0  # Если введено неверное значение, считаем 0%

        # Проверяем, что сумма процентов равна 100%
        if abs(total_percentage - 100.0) > 1e-6:  # Допускаем небольшую погрешность
            showwarning("Ошибка", f"Сумма процентов должна быть равна 100%. Сейчас: {total_percentage:.2f}%")

        else:
            showinfo("Успех", "Данные успешно сохранены!")

 

        
    def save_pressure(self,min_pressure_entry,max_pressure_entry,average_value_entry,status_label):
        try:
            # Получаем значения из полей ввода
            min_pressure = float(min_pressure_entry)
            average_value = float(average_value_entry)
            max_pressure = float(max_pressure_entry)
            print(max_pressure)
            # Проверяем корректность данных
            if not (min_pressure_entry.strip() and average_value_entry.strip() and max_pressure_entry.strip()):
                status_label.config(text="Ошибка: Введите значения")
                return None
            if min_pressure > max_pressure:
                status_label.config(text="Ошибка: Минимальное давление больше максимального.")
                return None

            if average_value <= 0:
                status_label.config(text="Ошибка: Шаг должен быть положительным числом.")
                return None
            # Создаем массив давлений
            input_pressure_range = np.arange(min_pressure, (max_pressure + average_value), average_value)

            # Преобразуем массив в список
            input_pressure_range = input_pressure_range.tolist()
            # Очищаем статус
            status_label.config(text="Данные успешно сохранены.")
            
            return input_pressure_range

        except ValueError:
            # Обрабатываем ошибку ввода
            status_label.config(text="Ошибка: Введите числовые значения.")
            return None



if __name__ == "__main__":
    root = tk.Tk()
    calculator = Calculate()
    app = GUI(root, calculator)
    root.mainloop()