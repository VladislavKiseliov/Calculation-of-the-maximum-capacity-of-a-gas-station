import math

import pandas as pd
from functools import lru_cache


def calculate_Ky(P_in, P_out, t_in_regulator, Relative_gas_density, Kv, count_lines,flag = False,T_out = 0,Di = 0):
    # Преобразование давлений в абсолютные значения
    p1 = 10.19815 * float(P_in) + 1  # Абсолютное давление газа на входе в регулятор
    p2 = 10.19815 * float(P_out) + 1  # Абсолютное давление газа на выходе из регулятора
    DP = p1 - p2  # Перепад давления на регулирующем органе регулятора
    
    # Рабочая температура перед регулятором
    T1 = ((T_out+(P_in-P_out) * Di) + 273) if flag else (273 + t_in_regulator)

    D= Relative_gas_density/1.2574
    # Удельный вес газа при нормальных условиях
    gn = 1.205 * D
    # Поправочный коэффициент на сжимаемость газа
    if (p1 - p2) / p1 < 0.08:
        E = 1
    else:
        E = 1 - 0.46 * ((p1 - p2) / p1)
    
    # Расчет расхода газа
    if DP > 0:
        if p2 > 0.5 * p1:
            Q = count_lines * (Kv * (514 * E * math.sqrt((DP * p1) / (gn * T1))) / 1.15)
        else:
            Q = count_lines * (Kv * (280 * p1 * math.sqrt(1 / (gn * T1))) / 1.15)
    else:
        Q =0

    return Q

def heat_balance(P_in,P_out,T_in,T_out,Boiler_capacity,Di,Ccp,typeCalculate = False):
    T_heat_exchanger = T_out+(P_in-P_out) * Di
    Q = (Boiler_capacity/(1163*0.000001*(T_heat_exchanger-T_in)*Ccp))
    # print(f"{(1163*0.0.000001*(T_heat_exchanger-T_in)*Ccp)=}")
    if typeCalculate:
        return Q
    else:
        return Q,T_heat_exchanger

@lru_cache(maxsize=128)
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


def data_frame(P_in,t_in,gas_compositio):
    # Загрузка данных
    df = pd.read_csv("SostavGaza.csv")
    
    # Преобразование в DataFrame
    data = pd.DataFrame(list(gas_compositio.items()), columns=["Компонент", "Содержание (%)"])

    percent_Content = pd.DataFrame(data)

    # Создание нового DataFrame на основе формул
    de_result = pd.DataFrame({
        "mole_fraction": percent_Content["Содержание (%)"]/100.0,  
        "хi_Tкрi": (percent_Content["Содержание (%)"]/100.0) * df["Крит. темп. Tкрi (К)"],  
        "хi_Ркрi": (percent_Content["Содержание (%)"]/100.0) * df["Крит. давл. Pкрi (МПа)"],  
        "хi_Мi": (percent_Content["Содержание (%)"]/100.0) * df["Моляр. масса Мi (кг/моль)"],
        "Xi_Zci": (percent_Content["Содержание (%)"]/100.0) / df["Фактор сжимаемости Zci"],  
        "плотность": (percent_Content["Содержание (%)"]/100.0)* df["Плотность ρi (кг/куб.м)"],
    
    })
    de_result["Обьемная доля"] = de_result["mole_fraction"]/df["Фактор сжимаемости Zci"]/de_result["Xi_Zci"].sum()
    de_result["ri_Zci"] = de_result["Обьемная доля"]/df["Фактор сжимаемости Zci"]
    #print(self.de_result)
    Tpk = de_result["хi_Tкрi"].sum()
    Ppk = de_result["хi_Ркрi"].sum()
    M= de_result["хi_Мi"].sum()
    Plotnost = de_result["плотность"].sum()
    # P_in=1.2
    # t_in=5
    # Константы
    R = 8.3143 / M
    P_pr = (P_in + 0.101325) / Ppk
    T_pr = (273.15 + t_in) / Tpk

    # Коэффициенты E
    E0 = 4.437 - 1.015 * T_pr + 0.591 * T_pr**2
    E1 = 3.29 - 11.37 / T_pr + 10.9 / T_pr**2
    E2 = 3.23 - 16.27 / T_pr + 25.48 / T_pr**2 - 11.81 / T_pr**3
    E3 = -0.214 + 0.908 / T_pr - 0.967 / T_pr**2

    # Теплоемкость
    Cp = R * (E0 + E1 * P_pr + E2 * P_pr**2 + E3 * P_pr**3)
    Ccp = (Cp/4.19)*Plotnost

    # Коэффициент динамической вязкости
    mu0 = (1.81 + 5.95 * T_pr) * 10**(-6)
    B1 = -0.67 + 2.36 / T_pr - 1.93 / T_pr**2
    B2 = 0.8 - 2.89 / T_pr + 2.65 / T_pr**2
    B3 = -0.1 + 0.354 / T_pr - 0.314 / T_pr**2
    mu = mu0 * (1 + B1 * P_pr + B2 * P_pr**2 + B3 * P_pr**3)

    # Коэффициенты H
    H0 = 24.96 - 20.3 * T_pr + 4.57 * T_pr**2
    H1 = 5.66 - 19.92 / T_pr + 16.89 / T_pr**2
    H2 = -4.11 + 14.68 / T_pr - 13.39 / T_pr**2
    H3 = 0.568 - 2 / T_pr + 1.79 / T_pr**2
    Di = (H0 + H1 * P_pr + H2 * P_pr**2 + H3 * P_pr**3)*1.1

    # Коэффициенты A
    A1 = -0.39 + 2.03 / T_pr - 3.16 / T_pr**2 + 1.09 / T_pr**3
    A2 = 0.0423 - 0.1812 / T_pr + 0.2124 / T_pr**2
    Z = 1 + A1 * P_pr + A2 * P_pr**2

    # Плотность рабочая
    rho_rab = (((Plotnost * (P_in + 0.101325)) / 0.1) * (293.15 / (273.15 + t_in)) )/ Z
    # Кинематическая вязкость
    nu = mu / rho_rab
    # print("_____________1_________")
    # print(de_result)
    #     # Вывод переменных с подписями
    # print(f"Tpk (псевдокритическая температура): {Tpk}")
    # print(f"Ppk (псевдокритическое давление): {Ppk}")
    # print(f"M (молекулярная масса смеси): {M}")
    # print(f"Plotnost (плотность смеси при стандартных условиях): {Plotnost}")

    # # Константы
    # print(f"R (универсальная газовая постоянная, деленная на M): {R}")
    # print(f"P_pr (приведенное давление): {P_pr}")
    # print(f"T_pr (приведенная температура): {T_pr}")

    # # Коэффициенты E
    # print(f"E0: {E0}")
    # print(f"E1: {E1}")
    # print(f"E2: {E2}")
    # print(f"E3: {E3}")

    # # Теплоемкость
    # print(f"Cp (изобарная теплоемкость): {Cp}")
    # print(f"Ccp (удельная теплоемкость): {Ccp}")

    # # Коэффициент динамической вязкости
    # print(f"mu0 (начальное значение динамической вязкости): {mu0}")
    # print(f"B1: {B1}")
    # print(f"B2: {B2}")
    # print(f"B3: {B3}")
    # print(f"mu (динамическая вязкость): {mu}")

    # # Коэффициенты H
    # print(f"H0: {H0}")
    # print(f"H1: {H1}")
    # print(f"H2: {H2}")
    # print(f"H3: {H3}")
    # print(f"Di (внутренний диаметр): {Di}")

    # # Коэффициенты A
    # print(f"A1: {A1}")
    # print(f"A2: {A2}")
    # print(f"Z (коэффициент сжимаемости): {Z}")

    # # Плотность рабочая
    # print(f"rho_rab (рабочая плотность): {rho_rab}")

    # # Кинематическая вязкость
    # print(f"nu (кинематическая вязкость): {nu}")

    
    return rho_rab,Z,Plotnost,Di,Ccp
