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
from matplotlib.colors import ListedColormap
from tkinter import ttk

from utils.GetFilePatch import GetFilePatch
from core.application_service import (
    CalculationApplicationService,
    prepare_line_plot_data,
    prepare_limiting_map_data,
)
from ..services.ui_service import TkUiService, UiService
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

    def __init__(
        self,
        initial_data,
        model,
        callback: CallbackRegistry,
        table_controller,
        max_performance,
        ui_service: UiService | None = None,
    ):
        self.logger = logging.getLogger("App.MainController")
        self.callback = callback
        self.initial_data = initial_data
        self.table_controller = table_controller
        self.model = model
        self.max_performance = max_performance
        self.ui = ui_service or TkUiService()
        self.app_service = CalculationApplicationService(model, max_performance, self.logger)
        self.logger.info("Главный контроллер запущен")
        self._register_callbacks()

    def _register_callbacks(self):
        """Register all application callbacks with the callback registry."""
        # Gas composition callbacks
        self.callback.register("save_gas_composition", self.gaz_window)
        self.callback.register("save_sostav_gaz",self.save_sostav_gaz)
        self.callback.register("save_gas_composition_to_csv", 
                              lambda: self.save_sostav_gaz(to_csv=True))
        self.callback.register("load_gas_composition_to_csv", self.load_sostav_gaz_csv)

        # Pressure range callbacks
        for pressure_type in ["input", "output"]:
            self.callback.register(f"{pressure_type}_pressure",
                                 lambda pt=pressure_type: self.button_window_pressure(pt))
        self.callback.register("save_pressure_range", self.save_pressure)

        # Temperature callbacks
        self.callback.register("create_window_temperature", self.create_window_temperature)
        self.callback.register("save_temperature",self.save_temperature)

        # Table management callbacks
        self.callback.register("create_table_window", self.create_table)
        self.callback.register("save_table", self.table_controller.save_table)
        self.callback.register("open_table", self.table_controller.open_table)

        # Calculation and file operations
        self.callback.register("Расчет", self.calculate)
        self.callback.register("Save_file", self.save_project)
        self.callback.register("Load_file", self.load_project)

    def button_window_pressure(self, title:str):
        """Setup pressure range input window with existing values."""
        init_presure = self.model.get_pressure_range(title)
        self.initial_data.create_window_pressure(title, init_presure)

    def save_pressure(self):
        """Save pressure range data with validation."""
        try:
            pressure_dict = self.initial_data.get_data_component("pressure")
            self.model.save_pressure_range(self.initial_data.title,pressure_dict)
            pressure_type = "Входное" if self.initial_data.title == "input" else "Выходное"
            self.ui.show_info("Успех", f"{pressure_type} давление успешно сохранено!")
            self.initial_data.pressure_window.destroy()

        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении давления - {e}")
            self.ui.show_warning("Ошибка", "При сохранении давления возникла ошибка. Проверьте логи и попробуйте снова")
            return
        
    def gaz_window(self):
        """Create gas composition input window."""
        try:
            data = self.model.load_gas_composition()
            self.initial_data.create_window_sostav_gaz(data)
        except Exception as e:
            self.logger.error(f"Не удалось открыть окно состава газа: {e}")

    def save_sostav_gaz(self, to_csv=False):
        """Save gas composition data to model and optionally to CSV."""
        try:
            gas_composition = self.initial_data.get_data_component("gas_composition")
            print(f"Cстав газа {gas_composition=}")
            self.model.save_sostav_gaz(gas_composition)

            if to_csv:
                file_path = GetFilePatch.get_file_patch_csv(title="Сохранить состав газа")
                if file_path:
                    self.model.save_gaz_to_csv(gas_composition,file_path)
                else:
                    self.ui.show_warning("Предупреждение", "Не выбран файл для сохранения")
                    return

            # Уведомляем пользователя об успешном сохранении
            self.ui.show_info("Успех", "Состав газа сохранен")

        except FileNotFoundError as fnf_error:
            self.logger.error(f"Файл не найден: {fnf_error}")
            return

        except Exception as e:
            self.logger.error(f"Не удалось сохранить состав газа: {e}")
            self.ui.show_warning("Ошибка", f"Не удалось сохранить в файл: {e}")

        self.initial_data.gas_window.destroy()

    def load_sostav_gaz_csv(self):
        """Load gas composition data from CSV file."""
        try:

            file_path = GetFilePatch.get_file_patch_csv()
            data = self.model.load_gaz_from_csv(file_path)
            self.initial_data.load_gas_composition_to_csv(data)

        except FileNotFoundError:
            self.ui.show_error("Отмена", "Сохранение отменено пользователем")

        except Exception as e:
            # Обрабатываем ошибки при загрузке
            self.logger.error(f"Не удалось загрузить из файла: {e}")
            self.ui.show_warning("Ошибка", f"Не удалось загрузить данные из файла: {e}")

    def create_window_temperature(self):
        """Create temperature input window with existing values."""
        temperature  = self.model.get_temperature()
        self.initial_data.create_window_temperature(temperature)

    def save_temperature(self):
        """Save temperature data with validation."""
        try:
            temperature = self.initial_data.get_data_component("temperature")
            self.model.save_temp(temperature)
            self.logger.info(f"Сохраняем температуру газа {temperature} в хранилище")
            self.ui.show_info("Успех", "Температура успешно сохранена!")
        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении температуры - {e}")
            self.ui.show_warning("Ошибка", "При сохранении температуры возникла ошибка. Проверьте логи и попробуйте снова")
    
        self.initial_data.temp_window.destroy() # Придумать как заменить для всех окон

    def create_table(self):
        """Create table management window."""
        tables = self.model.get_table_manager()
        self.table_controller.create_window_table(tables)

    def save_project(self):
        """Save project configuration via GUI dialog."""
        try:
            file_path = self.ui.ask_save_file(
                title="Сохранить проект",
                defaultextension=".json",
                initialdir="saves",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not file_path:
                return
            self.model.export_config(file_path)
            self.ui.show_info("Успех", "Конфигурация успешно сохранена")
        except Exception as e:
            self.logger.exception(f"Ошибка при сохранении проекта: {e}")
            self.ui.show_warning("Ошибка", f"Не удалось сохранить проект: {e}")

    def load_project(self):
        """Load project configuration via GUI dialog."""
        try:
            file_path = self.ui.ask_open_file(
                title="Загрузить проект",
                defaultextension=".json",
                initialdir="saves",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not file_path:
                return
            self.model.import_config(file_path)
            self.ui.show_info("Успех", "Данные успешно загружены")
        except Exception as e:
            self.logger.exception(f"Ошибка при загрузке проекта: {e}")
            self.ui.show_warning("Ошибка", f"Не удалось загрузить проект: {e}")

    def calculate(self):
        """Execute main calculation process and generate results."""
        try:
            result = self.app_service.run_full_calculation()
            self.logger.info(f"Сохранена результирующая таблица: \n{result.df_result}")
            self.create_plot(result.df_result, result.df_limiting)
            self.show_results_window(
                result.df_result,
                result.df_limiting,
                result.df_margin,
                result.df_final_long,
            )
        except Exception as e:
            self.logger.exception(f"Ошибка расчета: {e}")
            self.ui.show_error("Ошибка", f"Не удалось выполнить расчет: {e}")

    def create_plot(self, df_result: pd.DataFrame, df_limiting: pd.DataFrame):
        """Create and display final flow and limiting-table plots."""
        self.logger.info("Начало построения графиков")

        sorted_columns, input_pressure_labels, output_pressure_values, series_by_output = prepare_line_plot_data(df_result)
        self.logger.debug(f"Ось X (входные давления): {input_pressure_labels}")
        self.logger.debug(f"Ось Y (выходные давления): {output_pressure_values}")

        # Figure 1: final flow by output pressure
        plt.figure(figsize=(10, 6))
        for output_pressure in output_pressure_values:
            self.logger.debug(f"Построение линии для выходного давления: {output_pressure}")
            plt.plot(
                input_pressure_labels,
                series_by_output[output_pressure],
                marker="o",
                label=f"Pout={output_pressure}",
            )

        plt.title("Итоговый расход: зависимость от входного давления")
        plt.xlabel("Входное давление (МПа)")
        plt.ylabel("Q_final")
        plt.legend(title="Выходное давление")
        plt.grid(True, alpha=0.35)
        plt.tight_layout()

        # Figure 2: limiting-table map
        pin_labels, out_values, table_names, code_matrix = prepare_limiting_map_data(df_limiting)
        color_palette = [
            "#1b9e77",
            "#d95f02",
            "#7570b3",
            "#e7298a",
            "#66a61e",
            "#e6ab02",
            "#a6761d",
            "#666666",
        ]
        if len(table_names) > len(color_palette):
            # fallback extension with matplotlib default cycle tones
            color_palette.extend(
                [f"C{i}" for i in range(len(table_names) - len(color_palette))]
            )
        cmap = ListedColormap(color_palette[: len(table_names)])

        fig, ax = plt.subplots(figsize=(11, 5))
        image = ax.imshow(code_matrix, aspect="auto", interpolation="nearest", cmap=cmap)
        ax.set_title("Карта ограничивающих таблиц")
        ax.set_xlabel("Входное давление (МПа)")
        ax.set_ylabel("Выходное давление (МПа)")
        ax.set_xticks(range(len(pin_labels)))
        ax.set_xticklabels(pin_labels, rotation=45, ha="right")
        ax.set_yticks(range(len(out_values)))
        ax.set_yticklabels([str(v) for v in out_values])

        cbar = fig.colorbar(image, ax=ax, ticks=list(range(len(table_names))))
        cbar.ax.set_yticklabels(table_names)
        cbar.set_label("Ограничивающая таблица")
        fig.tight_layout()

        self.logger.info("Графики успешно построены. Отображение...")
        plt.show()

    def _show_dataframe_in_tree(self, parent, df: pd.DataFrame):
        """Render dataframe into a Treeview with scrollbars."""
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True)

        columns = ["index"] + [str(c) for c in df.columns]
        tree = ttk.Treeview(frame, columns=columns, show="headings")

        tree.heading("index", text="index")
        tree.column("index", width=120, stretch=True, anchor="center")
        for col in df.columns:
            col_name = str(col)
            tree.heading(col_name, text=col_name)
            tree.column(col_name, width=140, stretch=True, anchor="center")

        for idx, row in df.iterrows():
            values = [idx] + [row[col] for col in df.columns]
            tree.insert("", "end", values=values)

        y_scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        x_scroll = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def _export_dataframe_csv(self, df: pd.DataFrame, default_name: str):
        """Export dataframe to CSV selected by user."""
        file_path = self.ui.ask_save_file(
            title="Сохранить результаты в CSV",
            defaultextension=".csv",
            initialfile=default_name,
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if not file_path:
            return
        df.to_csv(file_path, index=True, encoding="utf-8-sig")
        self.ui.show_info("Успех", f"Файл сохранен: {file_path}")

    def show_results_window(
        self,
        df_result: pd.DataFrame,
        df_limiting: pd.DataFrame,
        df_margin: pd.DataFrame,
        df_final_long: pd.DataFrame,
    ):
        """Show final results in a dedicated window with export actions."""
        window = tk.Toplevel(self.initial_data.parent)
        window.title("Финальные результаты расчета")
        window.geometry("1200x700")

        actions = ttk.Frame(window)
        actions.pack(fill="x", padx=8, pady=8)

        ttk.Button(
            actions,
            text="Экспорт: итоговый расход",
            command=lambda: self._export_dataframe_csv(df_result, "final_flow.csv"),
        ).pack(side="left", padx=4)
        ttk.Button(
            actions,
            text="Экспорт: ограничения",
            command=lambda: self._export_dataframe_csv(df_limiting, "final_limiting.csv"),
        ).pack(side="left", padx=4)
        ttk.Button(
            actions,
            text="Экспорт: запас",
            command=lambda: self._export_dataframe_csv(df_margin, "final_margin.csv"),
        ).pack(side="left", padx=4)
        ttk.Button(
            actions,
            text="Экспорт: сводная",
            command=lambda: self._export_dataframe_csv(df_final_long, "final_summary.csv"),
        ).pack(side="left", padx=4)

        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=8, pady=8)

        tab_result = ttk.Frame(notebook)
        tab_limiting = ttk.Frame(notebook)
        tab_margin = ttk.Frame(notebook)
        tab_summary = ttk.Frame(notebook)

        notebook.add(tab_result, text="Итоговый расход")
        notebook.add(tab_limiting, text="Ограничения")
        notebook.add(tab_margin, text="Запас")
        notebook.add(tab_summary, text="Сводная")

        self._show_dataframe_in_tree(tab_result, df_result)
        self._show_dataframe_in_tree(tab_limiting, df_limiting)
        self._show_dataframe_in_tree(tab_margin, df_margin)
        self._show_dataframe_in_tree(tab_summary, df_final_long)
