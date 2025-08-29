"""
Gas Properties Calculation Component

This module contains the gas properties calculation interface component.
"""

import tkinter as tk
from tkinter import messagebox

import core.Calculate_file as Calculate_file
from ..main_window import WidgetFactory


class Calculation_gas_properties:
    """
    Component for gas properties calculation interface.
    
    Provides:
    - Input fields for pressure and temperature
    - Gas composition integration
    - Real-time calculation and results display
    """

    def __init__(self, parent, model):
        self.parent = parent
        self.data_model = model
        self.create_widgets()

    def create_widgets(self):
        """Create the gas properties calculation interface."""
        # Input labels and fields
        label_pressure = WidgetFactory.create_label(self.parent, "Давление, МПа", 0, 0)
        label_temperature = WidgetFactory.create_label(self.parent, "Температура, ℃", 1, 0)
        
        self.entry_pressure = WidgetFactory.create_entry(self.parent, 0, 1)
        self.entry_temperature = WidgetFactory.create_entry(self.parent, 1, 1)

        # Calculate button
        gas_button = WidgetFactory.create_Button(
            parent=self.parent, 
            label_text="Рассчитать", 
            row=2, 
            function=self.start
        )

        # Results display area
        self.gaz_text = tk.Text(self.parent, height=10, width=50, state="disabled")
        self.gaz_text.grid(row=0, column=3, rowspan=4, padx=10, pady=5, sticky="nsew")

        # Configure grid weights for proper resizing
        self.parent.grid_columnconfigure(3, weight=1)
        for i in range(4):
            self.parent.grid_rowconfigure(i, weight=1)

    def start(self):
        """Execute gas properties calculation and display results."""
        try:
            # Get input values
            p_in = float(self.entry_pressure.get())
            t_in = float(self.entry_temperature.get())
        except ValueError:
            self._display_error("Ошибка: Введите числовые значения для давления и температуры.")
            return

        try:
            # Get gas composition from model
            gas_composition = self.data_model.load_gas_composition()
            
            # Perform calculations
            rho_rab, z, plotnost, Di, Ccp = Calculate_file.data_frame(p_in, t_in, gas_composition)

            # Display results
            self._display_results(p_in, t_in, rho_rab, z, plotnost, Di, Ccp)
            
        except Exception as e:
            self._display_error(f"Ошибка при расчете: {str(e)}")

    def _display_results(self, p_in, t_in, rho_rab, z, plotnost, Di, Ccp):
        """Display calculation results in the text area."""
        self.gaz_text.config(state="normal")
        self.gaz_text.delete("1.0", tk.END)
        
        # Input data section
        self.gaz_text.insert(tk.END, "=== Введенные данные ===\n")
        self.gaz_text.insert(tk.END, f"Давление: {p_in} МПа\n")
        self.gaz_text.insert(tk.END, f"Температура: {t_in} ℃\n\n")
        
        # Results section
        self.gaz_text.insert(tk.END, "=== Результаты расчета ===\n")
        self.gaz_text.insert(tk.END, f"Плотность смеси при рабочих условиях: {rho_rab:.2f} кг/м³\n")
        self.gaz_text.insert(tk.END, f"Коэффициент сжимаемости: {z:.4f}\n")
        self.gaz_text.insert(tk.END, f"Плотность смеси при стандартных условиях: {plotnost:.4f} кг/м³\n")
        
        self.gaz_text.config(state="disabled")

    def _display_error(self, error_message):
        """Display error message in the text area."""
        self.gaz_text.config(state="normal")
        self.gaz_text.delete("1.0", tk.END)
        self.gaz_text.insert(tk.END, error_message)
        self.gaz_text.config(state="disabled")