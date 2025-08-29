"""
Heat Balance Calculation Component
"""

import tkinter as tk
import core.Calculate_file as Calculate_file
from ..main_window import WidgetFactory


class Heat_balance:
    """Component for heat balance calculation interface."""

    def __init__(self, parent, model):
        self.parent = parent
        self.data_model = model
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        """Create the heat balance calculation interface."""
        name_labels = [
            "Давление вход, МПа",
            "Давление выход, МПа",
            "Температура вход, ℃",
            "Температура выход, ℃",
            "Мощность котельной, кВт",
        ]
        
        for i, name in enumerate(name_labels):
            label = WidgetFactory.create_label(self.parent, name, i, 0)
            entry = WidgetFactory.create_entry(self.parent, i, 1)
            self.entries[name] = entry

        gas_button = WidgetFactory.create_Button(
            self.parent, "Рассчитать", len(name_labels), function=self.calc_heat_balance
        )

        self.heat_balance_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.heat_balance_text.grid(row=0, column=3, rowspan=len(name_labels) + 1, padx=10, pady=5, sticky="nsew")

    def calc_heat_balance(self):
        """Execute heat balance calculation."""
        try:
            input_values = {}
            for name, entry in self.entries.items():
                input_values[name] = float(entry.get())
            
            gas_composition = self.data_model.load_gas_composition()
            rho_rab_in, z_in, plotnost_in, Di_in, Cc_in = Calculate_file.data_frame(
                input_values["Давление вход, МПа"],
                input_values["Температура вход, ℃"],
                gas_composition,
            )
            
            q, T = Calculate_file.heat_balance(
                input_values["Давление вход, МПа"],
                input_values["Давление выход, МПа"],
                input_values["Температура вход, ℃"],
                input_values["Температура выход, ℃"],
                input_values["Мощность котельной, кВт"],
                Di_in,
                Cc_in,
            )

            self._display_results(input_values, q, T, Di_in)

        except ValueError:
            self._display_error("Ошибка: Введите числовые значения.")
        except Exception as e:
            self._display_error(f"Ошибка при расчете: {str(e)}")

    def _display_results(self, input_values, q, T, Di_in):
        """Display results."""
        self.heat_balance_text.config(state="normal")
        self.heat_balance_text.delete("1.0", tk.END)
        self.heat_balance_text.insert(tk.END, f"Входное давление: {input_values['Давление вход, МПа']} МПа\n")
        self.heat_balance_text.insert(tk.END, f"Выходное давление: {input_values['Давление выход, МПа']} МПа\n")
        self.heat_balance_text.insert(tk.END, f"Расход: {q:.2f} нм³/ч\n")
        self.heat_balance_text.insert(tk.END, f"Температура после теплообменника: {T:.2f} ℃\n")
        self.heat_balance_text.insert(tk.END, f"Коэффициент Джоуля-Томсона: {Di_in:.4f}\n")
        self.heat_balance_text.config(state="disabled")

    def _display_error(self, error_message):
        """Display error message."""
        self.heat_balance_text.config(state="normal")
        self.heat_balance_text.delete("1.0", tk.END)
        self.heat_balance_text.insert(tk.END, error_message)
        self.heat_balance_text.config(state="disabled")