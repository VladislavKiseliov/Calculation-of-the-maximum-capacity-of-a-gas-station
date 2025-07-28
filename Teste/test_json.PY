import pickle

class A:
    def __init__(self):
        self.a =5
    def prin(self):
        print("Good")

a=A()

print(f"{a=}")
serialized_manager = pickle.dumps(a)
print(f"{serialized_manager=}")
# Восстанавливаем объект
manager = pickle.loads(serialized_manager)
print(f"{manager=}")
print(manager.prin())

dic = {"in":0,"out":2}


for i in dic:
    print(i)






class DataSaverLoader:
    def __init__(self,data_model:Data_model):
        self.data_model = data_model
        self.input_pressure_range = []
        self.output_pressure_range = []
        self.gas_composition = {}
        self.name_table = {}
        self.temperature = []

    def update_data(self):
        # Используем деструктуризацию для получения данных
        self.input_pressure_range = self.data_model.get_input_pressure_range()
        self.output_pressure_range = self.data_model.get_output_pressure_range()
        self.gas_composition = self.data_model.data_gas_composition
        self.temperature = self.data_model.temperature
        # Обработка таблиц
        self.name_table = self.data_model.get_table_manager()
        self.table_name = {key: manager.get_table_type() for key, manager in self.name_table.items()}
        
    def to_dict(self):
        return {
            "gas_composition": self.gas_composition,
            "input_pressure_range": self.input_pressure_range,
            "output_pressure_range": self.output_pressure_range,
            "temperature": self.temperature,
            "table_name": self.table_name
        }
    
    def save_data(self):
        saves_dir = "Saves"
        os.makedirs(saves_dir, exist_ok=True)  # Создаем директорию, если её нет
        self.update_data()
        data_dict = self.to_dict()
        file_path = filedialog.asksaveasfilename(
                title="Сохранить файл",
                initialdir = saves_dir,
                defaultextension=".json",  # Расширение по умолчанию
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]  # Фильтр типов файлов
            )
        with open(file_path, 'w',encoding='utf-8') as outfile:
            json.dump(data_dict, outfile, indent=4, ensure_ascii=False)

    def load_data(self):
        file_path = filedialog.askopenfilename(
                title="Выберите файл для загрузки состава газа",
                defaultextension=".json",  # Расширение по умолчанию
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]  # Фильтр типов файлов
            )
        with open(file_path, 'r',encoding='utf-8') as outfile:
            data = json.load( outfile)
            # print(data["gas_composition"])
            print(data["input_pressure_range"])
            # print(data["output_pressure_range"])
            # # print(data["temperature"]["in"])
            # print(data["table_name"])

        # self.data_model.set_temperature(data["temperature"]["in"],data["temperature"]["out"])
        # self.data_model.data_gas_composition = data["gas_composition"]
        # print(f"{self.data_model.data_gas_composition=}")
    
        
        self.data_model.set_pressure_range("input",data["input_pressure_range"])
        self.data_model.set_pressure_range("output",data["output_pressure_range"])
        print(f"{self.data_model.get_input_pressure_range()=}")
        print(f"{self.data_model.get_output_pressure_range()=}")
        # print(f"{self.data_model.temperature=}")

