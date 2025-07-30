import pandas as pd
import sqlite3



db_path = "tables.db"  # Путь к файлу базы данных SQLite


table_name = "123"  # Имя таблицы, которую ищем

with sqlite3.connect(db_path) as conn:
    cursor = conn.cursor()
    statement = "SELECT name FROM sqlite_master WHERE type='table' AND name=?;"
    cursor.execute(statement, (table_name,))
    result = cursor.fetchone()
    print(result)
    if result:
        print(f"Table {table_name} exists.")
    else:
        print(f"Table {table_name} does not exist.")
 



# data = {
#     "Pin_1": [6786.318482, -216595.449124],
#     "Pin_2": [14146.501808, -535934.382736],
#     "Pin_3": [21076.824513, 1016182.05513],
#     "Pin_4": [28205.299595, 256177.653751],
#     "Pin_5": [35589.569714, 145924.458547]
# }

# data1 = {
#     "Pin_1": [14146.501808318482, -14146.501808449124],
#     "Pin_2": [14146.14146501808, -535934.1414501808],
#     "Pin_3": [21076.14146501808, 14146.50180805513],
#     "Pin_4": [28205.14146501808, 14146.501808653751],
#     "Pin_5": [35589.14146501808, 14146.501808458547]
#     }

# # Индексы строк
# index = ["pipii", "pup"]
# P_out = [0.6,0.7,0.8,0.9,1]
# # Создание DataFrame

# # table_name = f"table_{str(0.6).replace('.', '_')}"


# def save(name,data):
#     df = pd.DataFrame(data, index=index)
#     table_name = f"table_{str(name).replace('.', '_')}"
#     column = df.columns.tolist()
#     print(f"{column=}")
#     # Формируем SQL-определение столбцов
#     column_definition = ", ".join([f"{str(col).replace('.', '_')} REAL" for col in column])
#     column_definitions = "indi TEXT" + ", " +column_definition
#     print(f"{column_definitions=}")
#     with sqlite3.connect(db_path) as conn:
#         cursor = conn.cursor()
#         # create_table_query = f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
#         # cursor.execute(create_table_query)
#         # Добавляем данные из DataFrame
#         df.to_sql(table_name, conn, if_exists="append", index = True, index_label="Name table" )
#     print("good")

# for i in P_out:
#     save(i,data)
