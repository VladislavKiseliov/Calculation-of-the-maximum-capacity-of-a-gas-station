"""
Initial Data Component Module

This module contains the Initial_data class responsible for:
- Creating the initial data input interface
- Managing gas composition input dialogs
- Handling temperature and pressure range dialogs
- Coordinating with main application through callback system
"""

import contextlib
import math
import tkinter as tk
from tkinter import ttk
from typing import Dict, List

from ..main_window import WidgetFactory, CallbackRegistry
from tkinter.messagebox import showinfo, showwarning


class Initial_data:
    """
    Component for managing initial data input interface.
    
    Responsible for:
    - Main button interface for data input sections
    - Gas composition input dialog
    - Temperature input dialog  
    - Pressure range input dialogs
    """

    def __init__(self, parent, callback: CallbackRegistry):
        self.callback = callback
        self.parent = parent
        self.entries = {}  # Storage for form data
        self.callbacks = {}  # Storage for callbacks
        self.create_widgets()

    def create_widgets(self):
        """Create the main interface buttons for initial data input."""
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
            function=lambda: self.callback.trigger("create_table_window"),
        )
        self.calculate_button = WidgetFactory.create_Button(
            self.parent, 
            label_text="Автоматический расчет", 
            row=6,
            function=lambda: self.callback.trigger("Расчет")
        )

    def create_window_sostav_gaz(self, data: Dict[str, float]):
        """Create gas composition input dialog window."""
        self.gas_window = tk.Toplevel(self.parent)
        self.gas_window.title("Состав газа")

        # List of gas components with chemical formulas
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

        # Create labels and input fields for each component in two columns
        median = int((len(self.components) / 2.0)) - 1

        for i, component in enumerate(self.components):
            if i <= median:
                label = WidgetFactory.create_label(self.gas_window, component, i, 0)
                entry = WidgetFactory.create_entry(self.gas_window, i, 1)
            else:
                label = WidgetFactory.create_label(
                    self.gas_window, component, i - 15, 3
                )
                entry = WidgetFactory.create_entry(self.gas_window, i - 15, 4)

            # Fill with existing data if available
            if component in data:
                entry.delete(0, tk.END)
                entry.insert(0, str(data[component]))

            entry.bind("<KeyRelease>", self.update_total_percentage)
            self.entries[component] = entry

        # Create total percentage label
        self.total_label = WidgetFactory.create_label(
            parent=self.gas_window,
            label_text="Сумма: 0.0%",
            row=math.floor((len(self.components) / 2)),
            column=4,
        )
        
        # Update total percentage display
        self.update_total_percentage()
        self.row_last_components = math.ceil((len(self.components) / 2) + 1)

        # Create action buttons
        self.save_gaz_sostav_button = WidgetFactory.create_Button(
            self.gas_window,
            "Сохранить",
            self.row_last_components,
            function=lambda: self.callback.trigger("save_sostav_gaz"),
        )
        
        self.save_to_file_button = WidgetFactory.create_Button(
            parent=self.gas_window,
            label_text="Сохранить в файл",
            row=self.row_last_components + 1,
            function=lambda: self.callback.trigger("save_gas_composition_to_csv"),
        )
        
        self.load_from_file_button = WidgetFactory.create_Button(
            self.gas_window,
            "Открыть из файла",
            self.row_last_components + 2,
            function=lambda: self.callback.trigger("load_gas_composition_to_csv"),
        )

    def update_total_percentage(self, event=None):
        """Calculate and update the total percentage from all input fields."""
        total = 0.0
        for component, entry in self.entries.items():
            with contextlib.suppress(ValueError):
                value = float(entry.get())
                total += value
        # Update total label
        self.total_label.config(text=f"Сумма: {total:.4f}%")

    def load_gas_composition_to_csv(self,gaz_composition: Dict[str, float]):
        try:
            for component, entry in self.entries.items():
                if component in gaz_composition:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(gaz_composition[component]))
                    self.update_total_percentage()
            showinfo("Успех", "Состав газа сохранен")
        except Exception as e:
            showwarning("Ошибка", f"Не удалось загрузить данные из файла: {e}")
            raise

    def create_window_temperature(self,init_temperature):
        """Create temperature input dialog window."""
        self.temperature_entries = {}
        self.temp_window = tk.Toplevel(self.parent)
        self.temp_window.attributes("-topmost", True)
        self.temp_window.title("Температурный режим")

        # Create input fields for inlet and outlet temperatures
        for idx, (title, label_text) in enumerate(
            [("input", "Температура на входе"), ("output", "Температура на выходе")]
        ):
            WidgetFactory.create_label(
                parent=self.temp_window, label_text=label_text, row=idx
            )
            entry = WidgetFactory.create_entry(parent=self.temp_window, row=idx)
            self.temperature_entries[title] = entry

        if init_temperature:
            self.temperature_entries["input"].insert(0, init_temperature["input"])
            self.temperature_entries["output"].insert(0, init_temperature["output"])

        # Create save button
        save_temperature_button = WidgetFactory.create_Button(
            parent=self.temp_window,
            label_text="Сохранить", 
            row=3,
            function=lambda: self.callback.trigger("save_temperature")
        )

    def create_window_pressure(self, title,init_pressure : List[float]):
        """Create pressure range input dialog window."""
        self.title = title
        self.pressure_window = tk.Toplevel(self.parent)
        self.pressure_window.title(self.title)

        # Create input fields for pressure range parameters
        labels = ["Минимальное давление:", "Максимальное давление:", "Шаг значения"]
        self.pressure_entries = {}

        for i, label_text in enumerate(labels):
            ttk.Label(self.pressure_window, text=label_text).grid(
                row=i, column=0, padx=5, pady=5
            )
            entry = WidgetFactory.create_entry(self.pressure_window, row=i, column=1)
            self.pressure_entries[labels[i]] = entry
        if init_pressure:
            self.pressure_entries["Минимальное давление"].insert(
                0, min(init_pressure)
            )
            self.pressure_entries["Максимальное давление"].insert(
                0, max(init_pressure)
            )
            self.pressure_entries["Шаг значения"].insert(
                0, round(init_pressure[1] - init_pressure[0], 2)
            )


        # Create save button
        self.save_button = WidgetFactory.create_Button(
            parent=self.pressure_window,
            label_text="Сохранить",
            row=4,
            function=lambda: self.callback.trigger("save_pressure_range")
        )

    def get_data_component(self, component:str) -> Dict[str, float]:
        """Get data from gas station data."""
        if component == "pressure":
            try:
                data = {}
                for component, entry in self.pressure_entries.items():
                    if pressure := self.pressure_entries[component].get():
                        data[component] = float(entry.get().replace(",", "."))
                    else:
                        showwarning("Ошибка", f"Введите значение для {component}")
                        return
                return data
            except ValueError as e:
                showwarning("Ошибка", f"Введите корректные числовые значения! {e}")
                return


        elif component == "temperature":
            data = {}
            for component in self.temperature_entries:
                if temperature := self.temperature_entries[component].get():
                    data[component] = float(temperature.replace(",", "."))
                else:
                    showwarning("Ошибка", f"Введите значение для {component}")
                    return

            return data

        elif component == "gas_composition":
            data = {}
            for component, entry in self.temperature_entries.items():
                try:
                    data[component] = float(entry.get().replace(",", "."))
                except ValueError:
                    data[component] = 0.0

            return  data
        else:
            return {}



