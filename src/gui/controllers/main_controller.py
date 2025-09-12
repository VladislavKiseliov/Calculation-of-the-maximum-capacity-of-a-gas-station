"""
Main Controller Module

This module contains the MainController class responsible for:
- Coordinating all application components
- Managing callback registrations
- Handling business logic for gas composition, pressure, temperature
- Orchestrating calculation processes
- Managing data persistence operations
"""

import logging
import tkinter as tk
from typing import Dict

import pandas as pd
import matplotlib.pyplot as plt
from tkinter.messagebox import showinfo, showwarning
from tkinter import filedialog, messagebox

from utils.GetFilePatch import GetFilePatch
from ..main_window import CallbackRegistry


class MainController:
    """
    Main application controller that coordinates all components.
    
    Responsible for:
    - Registering all application callbacks
    - Managing data flow between components
    - Coordinating calculation processes
    - Handling user interactions and validation
    """

    def __init__(self, initial_data, model, callback: CallbackRegistry, table_controller, max_performance):
        self.logger = logging.getLogger("App.MainController")
        self.callback = callback
        self.initial_data = initial_data
        self.table_controller = table_controller
        self.model = model
        self.max_performance = max_performance
        self.logger.info("Главный контроллер запущен")
        self._register_callbacks()

    def _register_callbacks(self):
        """Register all application callbacks with the callback registry."""
        # Gas composition callbacks
        self.callback.register("save_gas_composition", self.gaz_window)
        self.callback.register("save_sostav_gaz", lambda: self.save_sostav_gaz(self.initial_data.entries))
        self.callback.register("save_gas_composition_to_csv", 
                              lambda: self.save_sostav_gaz(entries=self.initial_data.entries, to_csv=True))
        self.callback.register("load_gas_composition_to_csv", self.load_sostav_gaz_csv)

        # Pressure range callbacks
        for pressure_type in ["input", "output"]:
            self.callback.register(f"{pressure_type}_pressure",
                                 lambda pt=pressure_type: self.setup_button_pressure(pt))
        self.callback.register("save_pressure_range", self.save_pressure)

        # Temperature callbacks
        self.callback.register("create_window_temperature", self.create_window_temperature)
        self.callback.register("save_temperature", 
                              lambda: self.save_temperature(self.initial_data.temperature_entries))

        # Table management callbacks
        self.callback.register("create_table_window", self.create_table)
        self.callback.register("save_table", self.table_controller.save_table)
        self.callback.register("open_table", self.table_controller.open_table)

        # Calculation and file operations
        self.callback.register("Расчет", self.calculate)
        self.callback.register("Save_file", self.model.export_config)
        self.callback.register("Load_file", self.model.import_config)

    def setup_button_pressure(self, title):
        """Setup pressure range input window with existing values."""
        self.initial_data.create_window_pressure(title)
        
        # Load existing pressure range values if available
        if pressure_range := self.model.get_pressure_range(title):
            print(f"{pressure_range=}")
            self.initial_data.pressure_entries["Минимальное давление:"].insert(
                0, min(pressure_range)
            )
            self.initial_data.pressure_entries["Максимальное давление:"].insert(
                0, max(pressure_range)
            )
            self.initial_data.pressure_entries["Шаг значения"].insert(
                0, round(pressure_range[1] - pressure_range[0], 2)
            )

    def save_pressure(self):
        """Save pressure range data with validation."""
        min_pressure = self.initial_data.pressure_entries["Минимальное давление:"].get()
        max_pressure = self.initial_data.pressure_entries["Максимальное давление:"].get()
        step = self.initial_data.pressure_entries["Шаг значения"].get()
     
        try:
            if not all([min_pressure, max_pressure, step]):
                raise ValueError("Ошибка: Введите значения")
            
            self.model.save_pressure_range1(
                self.initial_data.title,
                float(min_pressure),
                float(max_pressure),
                float(step)   
            )
            
            pressure_type = "Входное" if self.initial_data.title == "input" else "Выходное"
            showinfo("Успех", f"{pressure_type} давление успешно сохранено!")
            self.initial_data.pressure_window.destroy()

        except ValueError as e:
            showwarning("Ошибка", f"Введите корректные числовые значения! {e}")
            return
        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении давления - {e}")
            showwarning("Ошибка", "При сохранении давления возникла ошибка. Проверьте логи и попробуйте снова")
            return
        
    def gaz_window(self):
        """Create gas composition input window."""
        data = self.model.load_gas_composition()
        self.initial_data.create_window_sostav_gaz(data)

    def save_sostav_gaz(self, entries: Dict[str, tk.Entry], to_csv=False):
        """Save gas composition data to model and optionally to CSV."""
        data = {component: entries[component].get() for component in entries}
        self.model.save_sostav_gaz(data)

        if to_csv:
            self.model.save_gaz_to_csv(data)

        self.initial_data.gas_window.destroy()


    def load_sostav_gaz_csv(self):
        """Load gas composition data from CSV file."""
        try:

            file_path = GetFilePatch.get_file_patch_csv()
            # Открываем проводник для выбора файла
            data = self.model.load_gaz_from_csv(file_path)

            for component, entry in self.initial_data.entries.items():
                if component in data:
                    entry.delete(0, tk.END)
                    entry.insert(0, str(data[component]))
                    self.initial_data.update_total_percentage()

        except FileNotFoundError:
            messagebox.showerror("Отмена", "Сохранение отменено пользователем")

        except Exception as e:
            # Обрабатываем ошибки при загрузке
            self.logger.error("Ошибка", f"Не удалось загрузить из файла: {e}")
            showwarning("Ошибка", f"Не удалось загрузить данные из файла: {e}")




    def create_window_temperature(self):
        """Create temperature input window with existing values."""
        self.initial_data.create_window_temperature()
        if temperature := self.model.get_temperature():
            self.initial_data.temperature_entries["input"].insert(0, temperature["input"])
            self.initial_data.temperature_entries["output"].insert(0, temperature["output"])
            self.logger.info(f"Окно температуры инициализировано с данными: {temperature}")
        else:
            self.logger.info("Окно температуры открыто без начальных данных")

    def save_temperature(self, temperature_entries: Dict[str, tk.Entry]):
        """Save temperature data with validation."""
        data = {}
        
        for component in temperature_entries:
            if temperature := temperature_entries[component].get():
                data[component] = float(temperature)
            else:
                showwarning("Ошибка", f"Введите значение для {component}")
                return

        try:
            self.model.save_temp(data)
            self.logger.info(f"Сохраняем температуру газа {data} в хранилище")
            showinfo("Успех", "Температура успешно сохранена!")
        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении температуры - {e}")
            showwarning("Ошибка", "При сохранении температуры возникла ошибка. Проверьте логи и попробуйте снова")
    
        self.initial_data.temp_window.destroy()

    def create_table(self):
        """Create table management window."""
        tables = self.model.get_table_manager()
        self.table_controller.create_window_table(tables)

    def calculate(self):
        """Execute main calculation process and generate results."""
        # Gather all required data
        input_pressure = self.model.get_pressure_range("input")
        output_pressure = self.model.get_pressure_range("output")
        tables = self.model.get_table_manager()
        temperature = self.model.get_temperature()
        gas_composition = self.model.load_gas_composition()
        
        # Get table data
        tables_data = {}
        for table_name in tables:
            tables_data[table_name] = self.model.get_table_data(table_name)
        
        self.logger.debug(f"Данные таблиц для расчета: {tables_data}")
        
        # Perform calculations for each output pressure
        df_result = pd.DataFrame()
        
        for P_out in output_pressure:
            df = self.max_performance.calculate(
                input_pressure,
                P_out,
                tables,
                temperature,
                gas_composition,
                tables_data
            )    
            
            # Save intermediate results
            self.model.save_intermedia(df, f"Промежуточный результат для P_out={P_out}", index_flag=True)
            
            # Get minimum values for this output pressure
            df_min = pd.DataFrame([df.min()])
            self.logger.debug(f"Результат расчета для {P_out=}: \n{df_min.to_string()}")
                
            # Set index and combine with main result
            df_min.index = [P_out] * len(df_min)
            df_result = pd.concat([df_result, df_min])
            self.logger.debug(f"Текущий результат: \n{df_result}")

        # Save final results
        self.model.save_intermedia(df_result, "Результирующая таблица")
        self.logger.info(f"Сохранена результирующая таблица: \n{df_result}")    
        
        # Create visualization
        self.create_plot(df_result, input_pressure, output_pressure)

    def create_plot(self, df_result: pd.DataFrame, input_pressures, output_pressures):
        """Create and display results plot."""
        self.logger.info("Начало построения графика")
        plt.figure(figsize=(10, 6))
        
        # Prepare data for plotting
        input_pressure_labels = [i.replace("Pin_", "") for i in df_result.columns]
        output_pressure_values = df_result.index.tolist()
        
        self.logger.debug(f"Ось X (входные давления): {input_pressure_labels}")
        self.logger.debug(f"Ось Y (выходные давления): {output_pressure_values}")

        # Plot lines for each output pressure
        for output_pressure in output_pressure_values:
            self.logger.debug(f"Построение линии для выходного давления: {output_pressure}")
            plt.plot(
                input_pressure_labels, 
                df_result.loc[output_pressure], 
                label=f"Выходное давление {output_pressure}"
            )
        
        # Configure plot
        plt.title("График зависимости расхода от входного давления")
        plt.xlabel("Входное давление (МПа)")
        plt.ylabel("Расход")
        plt.legend(title="Выходное давление")
        plt.grid(True)
        
        self.logger.info("График успешно построен. Отображение...")
        plt.show()