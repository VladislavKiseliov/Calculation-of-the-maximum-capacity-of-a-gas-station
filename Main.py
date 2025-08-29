import sys
import os
import tkinter as tk

# Добавляем путь к src в Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    """
    Главная функция запуска приложения с новой модульной структурой.
    """
    try:
        # Создаем корневое окно
        root = tk.Tk()
        
        # Импортируем компоненты из новой структуры
        from gui.main_window import GuiManager, CallbackRegistry
        from gui.components.initial_data import Initial_data
        from gui.controllers.main_controller import MainController
        from gui.controllers.table_controller import TableController
        from gui.tables.table_gui import GuiTable
        from gui.calculations.gas_properties import Calculation_gas_properties
        
        from core.DataModel import Data_model, DataStorage, CSVManager, DataBaseManager, JsonManager
        from core.calculate_Max_performance import Max_performance
        from utils.logger_config import setup_logger, create_log_file
        
        # Настраиваем логирование
        log_filename = create_log_file()
        logger = setup_logger(log_filename)
        logger.info("Запуск приложения расчета ГРС")
        
        # Инициализируем систему обратных вызовов
        callback_registry = CallbackRegistry()
        
        # Создаем GUI менеджер
        gui_manager = GuiManager(root, callback_registry)
        
        # Создаем компоненты для модели данных
        data_storage = DataStorage()
        csv_manager = CSVManager()
        database_manager = DataBaseManager()
        json_manager = JsonManager()
        
        # Инициализируем модель данных с зависимостями
        data_model = Data_model(data_storage, csv_manager, database_manager, json_manager)
        
        # Создаем экземпляр калькулятора производительности
        max_performance = Max_performance()
        
        # Настраиваем грид для главного окна
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Инициализируем компоненты GUI
        initial_data_frame = gui_manager.get_tab_frame("Исходные данные")
        initial_data = Initial_data(initial_data_frame, callback_registry)
        
        # Создаем GUI компоненты для таблиц
        gui_table = GuiTable(initial_data_frame, callback_registry)
        
        # Создаем контроллеры
        table_controller = TableController(gui_table, callback_registry, data_model)
        main_controller = MainController(
            initial_data, data_model, callback_registry, 
            table_controller, max_performance
        )
        
        # Инициализируем компоненты расчетов
        gas_properties_frame = gui_manager.get_tab_frame("Свойства газа")
        gas_properties = Calculation_gas_properties(gas_properties_frame, data_model)
        
        logger.info("Приложение успешно инициализировано")
        
        # Запускаем главный цикл приложения
        root.mainloop()
        
    except ImportError as e:
        error_msg = f"Ошибка импорта: {e}\nУбедитесь, что все файлы находятся в правильных папках"
        print(error_msg)
        try:
            tk.messagebox.showerror("Ошибка импорта", error_msg)
        except:
            pass
        sys.exit(1)
    except Exception as e:
        error_msg = f"Ошибка запуска приложения: {e}"
        print(error_msg)
        try:
            tk.messagebox.showerror("Ошибка запуска", error_msg)
        except:
            pass
        sys.exit(1)

if __name__ == "__main__":
    main()
