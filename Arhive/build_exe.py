import os
import subprocess
import sys

def build_exe():
    # Основной файл программы (точка входа)
    main_script = "main.py"

    # Дополнительные файлы программы
    additional_files = [
        "calc_regul.py",
        "gaz_library.py",
        "Heat_balance.py",
        "calc_tube.py",
        "SostavGaza.csv"
    ]

    # Команда для PyInstaller
    command = [
        "pyinstaller",
        "--onefile",  # Создание одного файла
        "--noconsole",  # Скрытие консольного окна (для GUI-приложений)
        "--name=MyProgram"  # Имя выходного файла
        "--hidden-import=pandas",  # Явное указание модуля
    ]

    # Добавление всех дополнительных файлов
    for file in additional_files:
        command.append(f"--add-data={file};.")

    # Добавление главного скрипта
    command.append(main_script)

    # Выполнение команды
    print("Начинаю сборку программы...")
    try:
        subprocess.run(command, check=True)
        print("Сборка завершена успешно!")
        print("Исполняемый файл находится в папке 'dist'.")
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при сборке: {e}")

if __name__ == "__main__":
    build_exe()