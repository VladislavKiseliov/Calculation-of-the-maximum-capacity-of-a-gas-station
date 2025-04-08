
def calc( pipe_diameter_mm, pipe_wall_thickness_mm, gas_pressure_mpa, gas_temperature_c,
             gas_flow_velocity_m_s, number_of_lines,compressibility_factor):
        # Расчет внутреннего диаметра
        inner_pipe_diameter_mm = pipe_diameter_mm - 2 * pipe_wall_thickness_mm

        # Расчет площади сечения (правильная формула)
        inner_diameter_m = inner_pipe_diameter_mm / 1000  # Переводим мм в метры
        pipe_cross_section_area_m2 = 0.785 * inner_diameter_m**2

        # Конвертация давления
        gas_pressure_kgf_cm2 = gas_pressure_mpa * 10.197162129779

        # Расчет расхода
        gas_flow_rate_m3s = gas_flow_velocity_m_s * pipe_cross_section_area_m2
        gas_flow_rate_m3h = gas_flow_rate_m3s * 3600

        # Итоговый расчет Q (уточненная формула)
        Q = number_of_lines * (
            gas_flow_rate_m3h
            * (gas_pressure_mpa + 0.101325)
            / (
                ((gas_temperature_c + 273.15) / 293.15)
                * compressibility_factor
                * 0.101325
            )
        )
        return Q

