import logging
import Calculate_file
from DataModel import CSVManager, Data_model, DataBaseManager, DataStorage, JsonManager
import pandas as pd



class Max_performance:
    def __init__(self,data_model:Data_model):
        self.logger = logging.getLogger("App.Max_performance")  # Дочерний логгер
        self.data_model = data_model

    def _get_data(self):# берем остольные данные из class Data Model
        self.input_pressure_range = self.data_model.get_pressure_range("input") #Диапазон входного давления
        self.output_pressure_range = self.data_model.get_pressure_range("output") #Диапазон выходного давления
        self.tables_data = self.data_model.get_table_manager() # Названия таблиц
        self.temperature = self.data_model.get_temperature()

    def _calculate_tube(self,col_pressure, data):
        _, z, *_ = self._calculate_propertys_gaz(col_pressure, data["gas_temperature"])
        return  float(Calculate_file.calc(
                data["pipe_diameter"], # Диаметр трубы
                data["wall_thickness"], # Толщина стенки
                col_pressure, # Давление на входе
                data["gas_temperature"], # Температура газа
                data["gas_speed"], # Скорость газа
                data["lines_count"], # Количество линий
                z
                 ))
                 
    def _calculate_regulator(self,col_pressure, p_out, data):
        *_,plotnost,Di_in,_= self._calculate_propertys_gaz(col_pressure, self.temperature["input"])
        return  float(Calculate_file.calculate_Ky(
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

    def _calculate_heat_balance(self,col_pressure, p_out, data):
        
        *_,Di_in,Ccp_in = self._calculate_propertys_gaz(col_pressure,self.temperature["input"]) #получаем свойства газа
        # *_, Ccp_out = self.calculate_propertys_gaz(p_out,float(self.data_model.temperature["out"])) #получаем свойства газа
      
        return  Calculate_file.heat_balance(
            col_pressure, # Давление на входе
            p_out, # Давление на выходе
            self.temperature["input"],
            self.temperature["output"],
            data["boiler_power"], # Мощность котла
            Di_in,
            Ccp_in,
            True
            )

    def _calculate_propertys_gaz(self,gas_pressure_mpa,gas_temperature_c):
        gas_composition = self.data_model.load_gas_composition() # Получаем состав газа
        rho_rab, z, plotnost,Di,Ccp = Calculate_file.data_frame(gas_pressure_mpa, gas_temperature_c, gas_composition)
        return  rho_rab, z, plotnost,Di,Ccp
    
    def _calculate_for_table(self, col_pressure, P_out, data, df, col_name, table_name, table_type):
        """Обрабатывает одну таблицу в зависимости от её типа."""
        try:
            match table_type:
                case "Таблица для регуляторов":
                    print(f"{self._calculate_regulator(col_pressure, P_out, data)=}")
                    df.at[table_name, col_name] = self._calculate_regulator(col_pressure, P_out, data)
                case "Таблицы для труб до регулятора" :
                    df.at[table_name, col_name]  = self._calculate_tube(col_pressure, data)
                case "Таблицы для труб после регулятора":
                    df.at[table_name, col_name] = self._calculate_tube(P_out, data)
                case "Таблица котельной":
                    df.at[table_name, col_name] = self._calculate_heat_balance(col_pressure,P_out, data)
                case _:
                    self.logger.warning(f"Неизвестный тип таблицы: {table_type}")

        except Exception as e:
            self.logger.error(f"Ошибка при расчёте таблицы '{table_name}': {e}")
            self.logger.exception(e)

    def _full_calculate(self, P_out: float) -> pd.DataFrame:
        self.logger.info(f"*** Начинаем полный расчет для P_out={P_out} МПа ***")

        try:
            # Создаем пустой DataFrame
            df = pd.DataFrame()
            self.logger.debug("Создан пустой DataFrame для результатов")

            # Обрабатываем каждую таблицу
            for table_name, table_info in self.tables_data.items():
                table_type = self.tables_data[table_name].get_table_type()
                self.logger.info(f"Обрабатываем таблицу '{table_name}' типа '{table_type}'")

                # Получаем данные таблицы
                data = self.data_model.get_table_data(table_name)
                self.logger.debug(f"Данные таблицы '{table_name}': {data}")

                # Итерация по входным давлениям
                input_pressures = [float(p) for p in self.input_pressure_range]

                for col_pressure in input_pressures:
                    self.logger.info(f"Обработка давления {col_pressure} МПа для таблицы '{table_name}'")
                    col_name = f"Pin_{str(col_pressure).replace('.', '_')}"
                    
                    self._calculate_for_table(col_pressure, P_out, data, df, col_name, table_name,table_type)
                    print(df)


            self.logger.info(f"Итоговый DataFrame: \n{df.to_string()}")
            
            # Формируем минимальные значения
            df_min = pd.DataFrame([df.min()])
            self.logger.info(f"Минимальные значения для P_out={P_out}: \n{df_min.to_string()}")
            
            # # Сохраняем промежуточный результат
            # self.save_result.save(df, f"Промежуточный результат для P_out={P_out}")
            # self.logger.info(f"Промежуточные результаты сохранены для P_out={P_out}")
            print(df_min)
            return df_min

        except Exception as e:
            self.logger.error(f"Критическая ошибка в full_calculate: {str(e)}")
            self.logger.exception(e)
            raise

    def result(self):
        # Получение данных из модели
        self.logger.debug("Загрузка данных из DataModel")
        self._get_data()
        self.logger.info(f"Диапазон входных давлений: {self.input_pressure_range}")
        self.logger.info(f"Диапазон выходных давлений: {self.output_pressure_range}")
        self.logger.info(f"Таблицы для расчета: {self.tables_data}")
        df_result = pd.DataFrame()
        for out_pressure in self.output_pressure_range:
                self.logger.info(f"Обработка выходного давления: {out_pressure} МПа")
                
                # Расчет минимальных значений
                df_min = self._full_calculate(out_pressure)
                self.logger.debug(f"Результат full_calculate для {out_pressure=}: \n{df_min.to_string()}")
                
                # Установка индекса
                df_min.index = [out_pressure] * len(df_min)
                self.logger.debug(f"Индекс установлен: {df_min.index.tolist()}")
                
                # Объединение с итоговой таблицей
                df_result = pd.concat([df_result, df_min])
                self.logger.debug(f"Текущий df_result после добавления данных: \n{df_result}")
                df_result.to_excel("output.xlsx", index=True)
                print(f"{df_result=}")
