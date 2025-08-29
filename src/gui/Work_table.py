import logging
import math
import tkinter as tk
from tkinter import ttk
from abc import ABC, abstractmethod
from utils import logger_config


class WidgetFactory:
    @staticmethod
    def create_entry(parent, row, column=1, padx=5, pady=5):
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


class BaseTableManager(ABC):
    def __init__(self, table_type):
        self.table_type = table_type

    @abstractmethod
    def get_columns(self) -> list:
        pass

    def get_table_type(self) -> str:
        return self.table_type

class RegulatorTableManager(BaseTableManager):
    def get_columns(self):
        return [ "kv", "lines_count"]

class BoilerTableManager(BaseTableManager):
    def get_columns(self):
        return ["boiler_power", "gas_temp_in", "gas_temp_out"]

class PipeTableManager(BaseTableManager):
    def get_columns(self):
        return [
            "pipe_diameter",
            "wall_thickness",
            "gas_speed",
            "gas_temperature",
            "lines_count",
        ]

class TableFactory:
    @staticmethod
    def create_table_manager(table_type):
        logger = logging.getLogger("App.TableFactory")  # Дочерний логгер
        logger.info(f"Запрос на создание менеджера таблицы типа: '{table_type}'")

        match table_type:
            case "Таблица для регуляторов":
                logger.info("Создан менеджер таблицы регуляторов")
                return RegulatorTableManager(table_type)

            case "Таблица котельной":
                logger.info("Создан менеджер таблицы котельной")
                return BoilerTableManager(table_type)

            case "Таблицы для труб до регулятора" | "Таблицы для труб после регулятора":
                logger.info(f"Создан менеджер таблицы труб: {table_type}")
                return PipeTableManager(table_type)

            case _:
                error_msg = f"Неизвестный тип таблицы: {table_type}"
                logger.error(error_msg)
                raise ValueError(error_msg)
