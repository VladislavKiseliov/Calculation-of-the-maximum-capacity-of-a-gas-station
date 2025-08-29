"""
Regulator Calculation Component

This module contains the regulator calculation interface component.
"""

import tkinter as tk

import core.Calculate_file as Calculate_file
from ..main_window import WidgetFactory


class Calculation_regulator:
    """
    Component for regulator calculation interface.
    
    Provides:
    - Input fields for regulator parameters
    - Flow calculation based on Kv values
    - Results display and validation
    """

    def __init__(self, parent, model):
        self.parent = parent
        self.data_model = model
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        """Create the regulator calculation interface."""
        # Input field labels
        name_labels = [
            "Давление вход, МПа",
            "Давление выход, МПа", 
            "Температура, ℃",
            "Kv",
            "Количество линий",
        ]
        
        # Create input fields
        for i, name in enumerate(name_labels):
            label = WidgetFactory.create_label(self.parent, name, i, 0)
            entry = WidgetFactory.create_entry(self.parent, i, 1)
            self.entries[name] = entry

        # Calculate button
        gas_button = WidgetFactory.create_Button(
            self.parent, 
            "Рассчитать", 
            len(name_labels), 
            function=self.calc_regul
        )

        # Results display area
        self.regul_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.regul_text.grid(row=0, column=3, rowspan=len(name_labels) + 1, padx=10, pady=5, sticky="nsew")

        # Configure grid weights
        self.parent.grid_columnconfigure(3, weight=1)
        for i in range(len(name_labels) + 1):
            self.parent.grid_rowconfigure(i, weight=1)

    def calc_regul(self):
        """Execute regulator calculation and display results."""
        try:
            # Get input values
            input_values = {}
            for name, entry in self.entries.items():
                value = float(entry.get())
                input_values[name] = value
            
            # Get gas composition
            gas_composition = self.data_model.load_gas_composition()
            
            # Calculate gas properties
            rho_rab, z, plotnost, Di, Ccp = Calculate_file.data_frame(
                input_values["Давление вход, МПа"],
                input_values["Температура, ℃"],
                gas_composition,
            )
            
            # Calculate flow through regulator
            q = Calculate_file.calculate_Ky(
                input_values["Давление вход, МПа"],
                input_values["Давление выход, МПа"],
                input_values["Температура, ℃"],
                plotnost,
                input_values["Kv"],
                input_values["Количество линий"],
            )

            # Display results
            self._display_results(input_values, q, rho_rab, z, plotnost)

        except ValueError:
            self._display_error("Ошибка: Введите числовые значения для всех полей.")
        except Exception as e:
            self._display_error(f"Ошибка при расчете: {str(e)}")

    def _display_results(self, input_values, q, rho_rab, z, plotnost):
        """Display calculation results."""
        self.regul_text.config(state="normal")
        self.regul_text.delete("1.0", tk.END)
        
        # Input data section
        self.regul_text.insert(tk.END, "=== Введенные данные ===\n")
        self.regul_text.insert(tk.END, f"Входное давление: {input_values['Давление вход, МПа']} МПа\n")
        self.regul_text.insert(tk.END, f"Выходное давление: {input_values['Давление выход, МПа']} МПа\n")
        self.regul_text.insert(tk.END, f"Температура: {input_values['Температура, ℃']} ℃\n")
        self.regul_text.insert(tk.END, f"Kv: {input_values['Kv']}\n")
        self.regul_text.insert(tk.END, f"Количество линий: {input_values['Количество линий']}\n\n")
        
        # Results section
        self.regul_text.insert(tk.END, "=== Результаты расчета ===\n")
        self.regul_text.insert(tk.END, f"Расход через регулятор: {q:.2f} нм³/ч\n")
        self.regul_text.insert(tk.END, f"Плотность при рабочих условиях: {rho_rab:.2f} кг/м³\n")
        self.regul_text.insert(tk.END, f"Коэффициент сжимаемости: {z:.4f}\n")
        self.regul_text.insert(tk.END, f"Плотность при стандартных условиях: {plotnost:.4f} кг/м³\n")
        
        self.regul_text.config(state="disabled")

    def _display_error(self, error_message):
        """Display error message."""
        self.regul_text.config(state="normal")
        self.regul_text.delete("1.0", tk.END)
        self.regul_text.insert(tk.END, error_message)
        self.regul_text.config(state="disabled")