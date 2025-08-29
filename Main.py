import sys
import os
import tkinter as tk

# Добавляем путь к src в Python path
src_path = os.path.join(os.path.dirname(__file__), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

def main():
    """
    Главная функция запуска приложения.
    """
    try:
        # Создаем корневое окно
        root = tk.Tk()
        
        # Импортируем и инициализируем главные классы
        from gui.Main import GuiManager, CallbackRegistry, Initial_data,TableController,Сontroller,GuiTable
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
        
        
        
        # Инициализируем начальные данные
        initial_data_frame = gui_manager.get_tab_frame("Исходные данные")
        initial_data = Initial_data(initial_data_frame, callback_registry)
        
        guitable = GuiTable(initial_data_frame, callback_registry)

        table_controller = TableController(guitable, callback_registry,data_model)
        controller = Сontroller(initial_data, data_model, callback_registry,table_controller,max_performance)
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
