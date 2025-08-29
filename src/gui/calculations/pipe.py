"""
Pipe Calculation Component
"""

import tkinter as tk
import core.Calculate_file as Calculate_file
from ..main_window import WidgetFactory


class Calculation_pipi:
    """Component for pipe calculation interface."""

    def __init__(self, parent, model):
        self.parent = parent
        self.data_model = model
        self.entries = {}
        self.create_widgets()

    def create_widgets(self):
        """Create the pipe calculation interface."""
        gas_button = WidgetFactory.create_Button(
            self.parent, "Рассчитать", 0, function=self.calc_tube
        )

        name_labels = [
            "Давление, МПа",
            "Температура, ℃",
            "Диаметр трубы, мм",
            "Толщина стенки трубы, мм",
            "Скорость газа в трубе, м/с",
            "Количество линий",
        ]
        
        start_row = 1
        for i, name in enumerate(name_labels):
            label = WidgetFactory.create_label(self.parent, name, start_row + i, 0)
            entry = WidgetFactory.create_entry(self.parent, start_row + i, 1)
            self.entries[name] = entry

        self.tube_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.tube_text.grid(row=start_row, column=3, rowspan=len(name_labels), padx=10, pady=5, sticky="nsew")

        # Configure grid weights
        self.parent.grid_columnconfigure(3, weight=1)
        for i in range(start_row, start_row + len(name_labels)):
            self.parent.grid_rowconfigure(i, weight=1)

    def calc_tube(self):
        """Execute pipe calculation."""
        try:
            input_values = {}
            for name, entry in self.entries.items():
                input_values[name] = float(entry.get())

            gas_composition = self.data_model.load_gas_composition()
            rho_rab, z, plotnost, Di, Ccp = Calculate_file.data_frame(
                input_values["Давление, МПа"],
                input_values["Температура, ℃"],
                gas_composition,
            )

            q = Calculate_file.calc(
                input_values["Диаметр трубы, мм"],
                input_values["Толщина стенки трубы, мм"],
                input_values["Давление, МПа"],
                input_values["Температура, ℃"],
                input_values["Скорость газа в трубе, м/с"],
                input_values["Количество линий"],
                z,
            )

            self.update_tube_text(q, plotnost)

        except ValueError:
            self.update_tube_text(error_message="Ошибка: Введите числовые значения.")
        except Exception as e:
            self.update_tube_text(error_message=f"Ошибка при расчете: {str(e)}")

    def update_tube_text(self, q=None, plotnost=None, error_message=None):
        """Update text area with results or error message."""
        self.tube_text.config(state="normal")
        self.tube_text.delete("1.0", tk.END)

        if error_message:
            self.tube_text.insert(tk.END, error_message)
        else:
            self.tube_text.insert(tk.END, f"Расход газа: {q:.2f} нм³/ч\n")
            self.tube_text.insert(tk.END, f"Плотность газа: {plotnost:.4f} кг/м³\n")

        self.tube_text.config(state="disabled")