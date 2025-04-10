import pandas as pd

# Исходные данные
data = [
    [8400, 8600, 8700],
    [400, 500, 600],
    [300, 200, 100],
]

# Диапазоны давлений (названия столбцов)
pressure = [7.4, 8.4, 6]
for j,col_name in enumerate(pressure):
     print(f"{j=} {col_name=}")

# Создание пустого DataFrame с заданными столбцами
df = pd.DataFrame(columns=pressure)

# # Заполнение DataFrame поэлементно через цикл
# for i, row in enumerate(data):  # Проходим по строкам
#     print(f"{row=}")
#     for j, col_name in enumerate(pressure):  # Проходим по столбцам
#         df.at[i, col_name] = row[j]  # Добавляем значение в ячейку

# print(df)


def func(x):
    return x+1 


# data = ["pep","hep","rep"]

# for i in data:
#     for j,col_name in enumerate(pressure):
#         df.at[i, col_name] = func(pressure[j])

# # print(df)




tables_name = {"Odin":"reglator","TOr":"tube before regulator","Loki":"tube after regulator"}
def function(x):
    return x*2


def full_calculate():
        
        df = pd.DataFrame(columns=pressure)

        for tabl in tables_name.keys():  

            for j,col_name in enumerate(pressure):

                match tables_name[tabl]:

                    case "reglator":

                        df.at[tabl, col_name]  = function(pressure[j])

                    case "tube before regulator":

                        df.at[tabl, col_name]  = 2*function(pressure[j])

                    case "tube after regulator":

                        df.at[tabl, col_name]  = 3*function(pressure[j])

                    case "heatbalace":

                        df.at[tabl, col_name]  = 4
        return df


pressure_out = [0.5,0.6,0.7]

def net():
        df_new = pd.DataFrame(columns = pressure)
        # print(df_new)
        frame = full_calculate()
        print( f"Изначальный {frame}")
        for i in pressure_out:
            column_names = frame.columns
            lst = [frame[column].min() for column in column_names]
            # print(lst)
            # print(column_names)
            df_new.loc[i] = [frame[column].min() for column in column_names]
            # df_new.loc[i] = pd.Series([frame[column].min() for column in column_names], index=column_names).T
            # df_new.index = [i]
            # print(df_new)
        return df_new

# frame = full_calculate()
res = net()
print(res)