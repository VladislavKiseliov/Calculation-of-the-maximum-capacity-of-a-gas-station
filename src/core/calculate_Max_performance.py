import logging
import core.Calculate_file as Calculate_file
from core.DataModel import CSVManager, Data_model, DataBaseManager, DataStorage, JsonManager
import pandas as pd
from typing import Dict, Any, List, Tuple
import time
from functools import lru_cache


class Max_performance:
    def __init__(self):
        self.logger = logging.getLogger("App.Max_performance")
        self._calculation_stats = {
            'tube_calculations': 0,
            'regulator_calculations': 0,
            'heat_balance_calculations': 0,
            'gas_properties_calls': 0
        }


    def _calculate_tube(self, col_pressure: float, data: Dict[str, Any]) -> float:
        """Расчет параметров трубы"""
        self._calculation_stats['tube_calculations'] += 1
        self.logger.debug(f"Расчет трубы: P={col_pressure} МПа, D={data['pipe_diameter']} мм, T={data['gas_temperature']}°C")
        
        try:
            _, z, *_ = self._calculate_propertys_gaz(col_pressure, data["gas_temperature"])
            self.logger.debug(f"Кеш: {self._calculate_propertys_gaz.cache_info()}")
            
            result = float(Calculate_file.calc(
                data["pipe_diameter"],      # Диаметр трубы
                data["wall_thickness"],     # Толщина стенки
                col_pressure,              # Давление на входе
                data["gas_temperature"],   # Температура газа
                data["gas_speed"],         # Скорость газа
                data["lines_count"],       # Количество линий
                z
            ))
            self.logger.debug(f"Кеш расчета трубы: {Calculate_file.calc.cache_info()}")
            self.logger.debug(f"Расчет трубы завершен: результат={result:.6f}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка расчета трубы (P={col_pressure} МПа): {e}")
            raise

    def _calculate_regulator(self, col_pressure: float, p_out: float, data: Dict[str, Any]) -> float:
        """Расчет параметров регулятора"""
        self._calculation_stats['regulator_calculations'] += 1
        self.logger.debug(f"Расчет регулятора: Pin={col_pressure} МПа, Pout={p_out} МПа")
        
        try:
            *_, plotnost, Di_in, _ = self._calculate_propertys_gaz(col_pressure, self.temperature["input"])
            self.logger.debug(f"Кеш: {self._calculate_propertys_gaz.cache_info()}")
            result = float(Calculate_file.calculate_Ky(
                col_pressure,
                p_out,
                self.temperature["input"],
                plotnost,
                data["kv"],
                data["lines_count"],
                True,
                self.temperature["output"],
                Di_in
            ))
            self.logger.debug(f"Расчет регулятора завершен: результат={result:.6f}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка расчета регулятора (Pin={col_pressure}, Pout={p_out}): {e}")
            raise
    
    def _calculate_heat_balanc(self, col_pressure: float, p_out: float):
        """Расчет теплового баланса с использованием загруженных данных котельной"""
        self.logger.debug(f"Расчет теплового баланса из файла: Pin={col_pressure} МПа, Pout={p_out} МПа")
        
        try:
            # Получаем данные котельной из базы данных
            boiler_data = self.model.get_table_data("Boiler_data")
            
            if not boiler_data:
                self.logger.error("Данные котельной не найдены в базе данных")
                raise ValueError("Данные котельной не загружены")
            
            # Формируем ключи для поиска данных
            col_name = f"Pin_{str(col_pressure).replace('.', '_')}"
            row_key = f"Pout_{p_out}"
            
            # Ищем соответствующую строку по выходному давлению
            target_row = None
            for row in boiler_data:
                if row.get('index') == row_key:  # index содержит Pout_X.X
                    target_row = row
                    break
            
            if not target_row:
                self.logger.warning(f"Данные для Pout={p_out} не найдены, используем ближайшие значения")
                # Попытка найти ближайшее значение давления
                target_row = self._find_nearest_pressure_data(boiler_data, p_out)
            
            if not target_row:
                self.logger.error(f"Не удалось найти данные котельной для Pout={p_out}")
                raise ValueError(f"Данные для выходного давления {p_out} МПа не найдены")
            
            # Извлекаем данные для конкретного входного давления
            if col_name not in target_row:
                self.logger.warning(f"Данные для Pin={col_pressure} не найдены, используем интерполяцию")
                result = self._interpolate_boiler_data(target_row, col_pressure)
            else:
                # Парсим JSON данные из ячейки
                import json
                cell_data = json.loads(target_row[col_name])
                nm3h = cell_data['Nm3h']
                c_value = cell_data['C']
                
                self.logger.debug(f"Найдены данные котельной: Nm3h={nm3h}, C={c_value}")
                result = float(nm3h)  # Возвращаем расход
            
            self.logger.debug(f"Расчет теплового баланса завершен: результат={result:.6f}")
            return result
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета теплового баланса из файла (Pin={col_pressure}, Pout={p_out}): {e}")
            # Fallback к стандартному расчету
            return self._calculate_heat_balance_fallback(col_pressure, p_out)



    def _calculate_heat_balance(self, col_pressure: float, p_out: float, data: Dict[str, Any]) -> float:
        """Расчет теплового баланса"""
        self._calculation_stats['heat_balance_calculations'] += 1
        self.logger.debug(f"Расчет теплового баланса: Pin={col_pressure} МПа, Pout={p_out} МПа")

        try:
            *_, Di_in, Ccp_in = self._calculate_propertys_gaz(col_pressure, self.temperature["input"])
            result = Calculate_file.heat_balance(
                col_pressure,              # Давление на входе
                p_out,                     # Давление на выходе
                self.temperature["input"], # Температура на входе
                self.temperature["output"], # Температура на выходе
                data["boiler_power"],      # Мощность котла
                Di_in,
                Ccp_in,
                True
            )
            self.logger.debug(f"Расчет теплового баланса завершен: результат={result:.6f}")
            return result
        except Exception as e:
            self.logger.error(f"Ошибка расчета теплового баланса (Pin={col_pressure}, Pout={p_out}): {e}")
            raise
    
    @lru_cache(maxsize=128)
    def _calculate_propertys_gaz(self, gas_pressure_mpa: float, gas_temperature_c: float) -> Tuple:
        """Расчет свойств газа"""
        self._calculation_stats['gas_properties_calls'] += 1
        self.logger.debug(f"Расчет свойств газа: P={gas_pressure_mpa} МПа, T={gas_temperature_c}°C")
        
        try:
            gas_composition = self.gas_composition
            rho_rab, z, plotnost, Di, Ccp = Calculate_file.data_frame(
                gas_pressure_mpa, gas_temperature_c, gas_composition
            )
            
            self.logger.debug(f"Свойства газа рассчитаны: rho={rho_rab:.6f}, z={z:.6f}")
            return rho_rab, z, plotnost, Di, Ccp
            
        except Exception as e:
            self.logger.error(f"Ошибка расчета свойств газа (P={gas_pressure_mpa}, T={gas_temperature_c}): {e}")
            raise

    def _calculate_for_table(self, col_pressure: float, P_out: float, data: Dict[str, Any], 
                           df: pd.DataFrame, col_name: str, table_name: str, table_type: str):
        """Обрабатывает одну таблицу в зависимости от её типа."""
        self.logger.info(f"Обработка таблицы '{table_name}' ({table_type}): "
                        f"Pin={col_pressure} МПа, Pout={P_out} МПа, колонка='{col_name}'")
        
        try:
            result = None
            match table_type:
                case "Таблица для регуляторов":
                    result = self._calculate_regulator(col_pressure, P_out, data)
                    self.logger.debug(f"Регулятор: {result}")
                    
                case "Таблицы для труб до регулятора":
                    result = self._calculate_tube(col_pressure, data)
                    self.logger.debug(f"Труба до регулятора: {result}")
                    
                case "Таблицы для труб после регулятора":
                    result = self._calculate_tube(P_out, data)
                    self.logger.debug(f"Труба после регулятора: {result}")
                    

                    
                case "Таблица котельной":
                    result = self._calculate_heat_balanc(col_pressure, P_out)
                    # result = self._calculate_heat_balance(col_pressure, P_out, data)
                    self.logger.debug(f"Котельная: {result}")
                    
                case _:
                    self.logger.warning(f"Неизвестный тип таблицы: {table_type}")
                    return

            if result is not None:
                df.at[table_name, col_name] = result
                self.logger.info(f"Успешно рассчитано для '{table_name}'[{col_name}]: {result:.6f}")

        except Exception as e:
            error_msg = f"Ошибка при расчёте таблицы '{table_name}' (Pin={col_pressure}, Pout={P_out}): {e}"
            self.logger.error(error_msg)
            self.logger.exception(e)

    def _full_calculate(self, P_out: float,table_data,tables) -> pd.DataFrame:
        """Основной метод расчета"""
        start_time = time.time()
        self.logger.info("=" * 60)
        self.logger.info("НАЧАЛО ПОЛНОГО РАСЧЕТА")
        self.logger.info(f"Давление на выходе: {P_out} МПа")
        self.logger.info(f"Диапазон входных давлений: {self.input_pressure_range}")
        self.logger.info(f"Количество таблиц: {len(tables)}")
        self.logger.info("=" * 60)

        try:
            # Создаем пустой DataFrame
            df = pd.DataFrame()
            self.logger.debug("Создан пустой DataFrame для результатов")

            # Сбрасываем статистику
            for key in self._calculation_stats:
                self._calculation_stats[key] = 0

            table_counter = 0
            total_tables = len(tables)
            
            # Обрабатываем каждую таблицу
            for table_name in tables:
                table_counter += 1
                table_type = tables[table_name].get_table_type()
                self.logger.info(f"[{table_counter}/{total_tables}] Обрабатываем таблицу '{table_name}' типа '{table_type}'")


                # Итерация по входным давлениям
                input_pressures = [float(p) for p in self.input_pressure_range]
                pressure_counter = 0
                total_pressures = len(input_pressures)

                for col_pressure in input_pressures:
                    pressure_counter += 1
                    self.logger.debug(f"[{pressure_counter}/{total_pressures}] Обработка давления {col_pressure} МПа для таблицы '{table_name}'")
                    
                    col_name = f"Pin_{str(col_pressure).replace('.', '_')}"
                    self._calculate_for_table(col_pressure, P_out, table_data[table_name], df, col_name, table_name, table_type)

            # Логируем статистику
            execution_time = time.time() - start_time
            self._log_calculation_statistics(execution_time)
            
            return df

        except Exception as e:
            self.logger.critical(f"КРИТИЧЕСКАЯ ОШИБКА В ПОЛНОМ РАСЧЕТЕ: {str(e)}")
            self.logger.exception(e)
            raise

    def _log_calculation_statistics(self, execution_time: float):
        """Логирование статистики расчета"""
        stats = self._calculation_stats
        
        self.logger.info("=" * 60)
        self.logger.info("СТАТИСТИКА РАСЧЕТА:")
        self.logger.info(f"Время выполнения: {execution_time:.2f} секунд")
        self.logger.info(f"Расчеты труб: {stats['tube_calculations']}")
        self.logger.info(f"Расчеты регуляторов: {stats['regulator_calculations']}")
        self.logger.info(f"Расчеты теплового баланса: {stats['heat_balance_calculations']}")
        self.logger.info(f"Вызовы свойств газа: {stats['gas_properties_calls']}")
        self.logger.info("=" * 60)




    def calculate(self,p_in: list, p_out: float , tables: dict, 
                 temperature: dict, gas_composition: dict, table_data) -> pd.DataFrame:
        """
        Выполняет расчет максимальной производительности
        """
        self.logger.info("ЗАПУСК РАСЧЕТА МАКСИМАЛЬНОЙ ПРОИЗВОДИТЕЛЬНОСТИ")
        
        
        # Валидация входных данных
        if not all([p_in, tables, temperature, gas_composition, table_data]):
            raise ValueError("Все параметры должны быть заданы")
       
        # Установка параметров
        self.input_pressure_range = p_in
        self.tables_data = tables
        self.temperature = temperature
        self.gas_composition = gas_composition
        print(f"{self.input_pressure_range=}")

        try:
            result = self._full_calculate(p_out,table_data,tables)
            self.logger.info("РАСЧЕТ УСПЕШНО ЗАВЕРШЕН")
            return result
        
        except Exception as e:
            self.logger.error(f"Ошибка при выполнении расчета: {e}")
            raise