import json
import os
from tkinter import filedialog
import pandas as pd
import sqlite3

# # Исходные данные
# data = [
#     [8400, 8600, 8700],
#     [400, 500, 600],
#     [300, 200, 100],
# ]

# # Диапазоны давлений (названия столбцов)
# pressure = [7.4, 8.4, 6]
# for j,col_name in enumerate(pressure):
#      print(f"{j=} {col_name=}")

# # Создание пустого DataFrame с заданными столбцами
# df = pd.DataFrame(columns=pressure)

# # # Заполнение DataFrame поэлементно через цикл
# # for i, row in enumerate(data):  # Проходим по строкам
# #     print(f"{row=}")
# #     for j, col_name in enumerate(pressure):  # Проходим по столбцам
# #         df.at[i, col_name] = row[j]  # Добавляем значение в ячейку

# # print(df)


# def func(x):
#     return x+1


# # data = ["pep","hep","rep"]

# # for i in data:
# #     for j,col_name in enumerate(pressure):
# #         df.at[i, col_name] = func(pressure[j])

# # # print(df)


# tables_name = {"Odin":"reglator","TOr":"tube before regulator","Loki":"tube after regulator"}
# def function(x):
#     return x*2


# def full_calculate():

#         df = pd.DataFrame(columns=pressure)

#         for tabl in tables_name.keys():

#             for j,col_name in enumerate(pressure):

#                 match tables_name[tabl]:

#                     case "reglator":

#                         df.at[tabl, col_name]  = function(pressure[j])

#                     case "tube before regulator":

#                         df.at[tabl, col_name]  = 2*function(pressure[j])

#                     case "tube after regulator":

#                         df.at[tabl, col_name]  = 3*function(pressure[j])

#                     case "heatbalace":

#                         df.at[tabl, col_name]  = 4
#         return df


# pressure_out = [0.5,0.6,0.7]

# def net():
#         df_new = pd.DataFrame(columns = pressure)
#         # print(df_new)
#         frame = full_calculate()
#         print( f"Изначальный {frame}")
#         for i in pressure_out:
#             column_names = frame.columns
#             lst = [frame[column].min() for column in column_names]
#             # print(lst)
#             # print(column_names)
#             df_new.loc[i] = [frame[column].min() for column in column_names]
#             # df_new.loc[i] = pd.Series([frame[column].min() for column in column_names], index=column_names).T
#             # df_new.index = [i]
#             # print(df_new)
#         return df_new

# # frame = full_calculate()
# res = net()
# print(res)


db_path = "tables.db"  # Путь к файлу базы данных SQLite

df = pd.read_excel(
    r"C:\Users\RGG\Desktop\Calculate\Calculation-of-the-maximum-capacity-of-a-gas-station\Teste\data.xlsx",
    engine="openpyxl",
)
grouped = df.groupby('MPAout')

filtered_data = pd.DataFrame
with sqlite3.connect(db_path) as conn:
    for outpressure,group_data in grouped:

        filtered_data = group_data[['Mpainput', 'Nm3h', 'C']]
        print(filtered_data)

        filtered_data.to_sql(str(outpressure), conn, if_exists="replace",index = False)


saves_dir = "Saves"
os.makedirs(saves_dir, exist_ok=True)  # Создаем директорию, если её нет

file_path = filedialog.asksaveasfilename(
    title="Сохранить файл",
    initialdir=saves_dir,
    defaultextension=".json",  # Расширение по умолчанию
    filetypes=[
        ("JSON files", "*.json"),
        ("All files", "*.*"),
    ],  # Фильтр типов файлов
)
with open(file_path, "w", encoding="utf-8") as outfile:
    # json.dump(data, outfile, indent=4, ensure_ascii=False)
    # filtered_data.to_json()
    filtered_data.to_json('data.json')

restored_df = pd.read_json('data.json', orient='records')
print(f"{restored_df=}")















# result = df["MPAout"].unique()
# # res = df[["MPainput","Nm3/h(gas)"]]
# print(df)
# print(result)


# for i in result:
#     fd = df[df["MPAout"] == i][['Mpainput','Nm3h','C']]

#     print(fd)
#     column = fd.columns.tolist()
#     # Формируем SQL-определение столбцов
#     column_definitions = ", ".join([f"{str(col)} REAL" for col in column])
#     with sqlite3.connect(db_path) as conn:

#         cursor = conn.cursor()

#         create_table_query = f"CREATE TABLE IF NOT EXISTS \"{i}\" (table_name TEXT,{column_definitions})"

#         cursor.execute(create_table_query)
#         # Добавляем данные из DataFrame

#     fd.to_sql(str(i), conn, if_exists="replace",index = False)







