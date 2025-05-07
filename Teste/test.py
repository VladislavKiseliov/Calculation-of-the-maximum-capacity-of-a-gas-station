
import pandas as pd
import matplotlib.pyplot as plt

# Пример DataFrame
# data = {
#     "Входное давление": ["1.0", "2.0", "3.0", "4.0", "5.0"],
#     "0.2": [7153.621616,  13733.459758,  20447.459022,  27363.961366,  34552.61222],
#     "0.4": [7153.621616,  13733.459758,  20447.459022 , 27363.961366,  34552.61222],
#     "0.6": [6597.767384,  13733.459758,  20447.459022,  27363.961366,  34552.61222],
# }



# df = pd.DataFrame(data)

# # Извлечение данных
# input_pressure = df["Входное давление"]  # Ось X
# output_pressures = df.columns[1:]        # Названия столбцов для выходных давлений

# # Построение графика
# plt.figure(figsize=(10, 6))

# for output_pressure in output_pressures:
#     plt.plot(input_pressure, df[output_pressure], label=output_pressure)

# # Настройка графика
# plt.title("График зависимости расхода от входного давления")
# plt.xlabel("Входное давление (МПа)")
# plt.ylabel("Расход")
# plt.legend(title="Выходное давление")
# plt.grid(True)

# # Отображение графика
# plt.show()


table = {"name":[1,2]}
# data = [1,2,3,4,5]
# print(table["name"])
# print(table["name"][0])
# for i in data:
#     print(lambda x=i: print(x))
# Распаковка ключа
[yiti] = table
print(f"{yiti=}")
# Получение значения
value = table[yiti]

print(yiti,value)


stroke = "1.5"
# get()

a = float(stroke.replace(",","."))

print(a,type(a))

tables = {"Таблица для регуляторов":12, "Таблица котельной":13}

for name in tables:
    print(name)

tabl = {"fdkls":12}
print(tables)

tables.update(tabl)

print(tables)