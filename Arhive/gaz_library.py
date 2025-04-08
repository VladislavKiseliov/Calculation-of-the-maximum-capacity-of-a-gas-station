
import pandas as pd



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
    Ccp = Cp/(4.19*Plotnost)

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
    Di = H0 + H1 * P_pr + H2 * P_pr**2 + H3 * P_pr**3

    # Коэффициенты A
    A1 = -0.39 + 2.03 / T_pr - 3.16 / T_pr**2 + 1.09 / T_pr**3
    A2 = 0.0423 - 0.1812 / T_pr + 0.2124 / T_pr**2
    Z = 1 + A1 * P_pr + A2 * P_pr**2

    # Плотность рабочая
    rho_rab = (Plotnost * (P_in + 0.101325) / 0.1) * (293.15 / (273.15 + t_in)) * (1 / Z)
    # Кинематическая вязкость
    nu = mu / rho_rab

    return rho_rab,Z,Plotnost,Di,Ccp
