import logging
from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class BaseTableManager:
    table_type: str
    columns: Tuple[str, ...] = field(default_factory=tuple)

    def get_table_type(self) -> str:
        return self.table_type

    def get_columns(self) -> list:
        return list(self.columns)


@dataclass
class RegulatorTableManager(BaseTableManager):
    columns: Tuple[str, ...] = ("kv", "lines_count")


@dataclass
class BoilerTableManager(BaseTableManager):
    columns: Tuple[str, ...] = ("boiler_power", "gas_temp_in", "gas_temp_out")


@dataclass
class PipeTableManager(BaseTableManager):
    columns: Tuple[str, ...] = (
        "pipe_diameter",
        "wall_thickness",
        "gas_speed",
        "gas_temperature",
        "lines_count",
    )


class TableFactory:
    @staticmethod
    def create_table_manager(table_type):
        logger = logging.getLogger("App.TableFactory")
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
