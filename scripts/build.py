#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Скрипт сборки проекта калькулятора ГРС.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(command, description):
    """Выполняет команду и выводит результат."""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} - успешно")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - ошибка: {e}")
        print(f"Вывод: {e.stdout}")
        print(f"Ошибки: {e.stderr}")
        return False

def check_dependencies():
    """Проверяет наличие необходимых зависимостей."""
    print("📋 Проверка зависимостей...")
    
    # Проверяем Python
    python_version = sys.version_info
    if python_version < (3, 8):
        print(f"❌ Требуется Python 3.8+, найден {python_version.major}.{python_version.minor}")
        return False
    
    print(f"✅ Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Проверяем установленные пакеты
    required_packages = ['pandas', 'numpy', 'matplotlib', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - не установлен")
    
    if missing_packages:
        print(f"⚠️  Отсутствующие пакеты: {', '.join(missing_packages)}")
        print("Установите их командой: pip install " + " ".join(missing_packages))
        return False
    
    return True

def create_executable():
    """Создает исполняемый файл с помощью PyInstaller."""
    if not shutil.which('pyinstaller'):
        print("⚠️  PyInstaller не найден. Установите его: pip install pyinstaller")
        return False
    
    command = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name=GasCalculator',
        '--add-data=data;data',
        '--add-data=config;config',
        'main.py'
    ]
    
    return run_command(' '.join(command), "Создание исполняемого файла")

def run_tests():
    """Запускает тесты проекта."""
    if os.path.exists('tests'):
        return run_command('python -m pytest tests/', "Выполнение тестов")
    else:
        print("⚠️  Папка tests не найдена, пропускаем тесты")
        return True

def clean_build():
    """Очищает временные файлы сборки."""
    print("🧹 Очистка временных файлов...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    files_to_clean = ['*.spec']
    
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🗑️  Удалена папка {dir_name}")
    
    # Очистка __pycache__ во всех подпапках
    for root, dirs, files in os.walk('.'):
        for dir_name in dirs:
            if dir_name == '__pycache__':
                full_path = os.path.join(root, dir_name)
                shutil.rmtree(full_path)
                print(f"🗑️  Удалена папка {full_path}")

def main():
    """Главная функция сборки."""
    print("🚀 Начало сборки проекта калькулятора ГРС")
    print("=" * 50)
    
    # Проверяем зависимости
    if not check_dependencies():
        print("❌ Сборка прервана из-за отсутствующих зависимостей")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Очищаем предыдущие сборки
    clean_build()
    
    print("\n" + "=" * 50)
    
    # Запускаем тесты
    if not run_tests():
        print("⚠️  Тесты не прошли, но продолжаем сборку")
    
    print("\n" + "=" * 50)
    
    # Создаем исполняемый файл
    if create_executable():
        print("🎉 Сборка завершена успешно!")
        print("📦 Исполняемый файл находится в папке dist/")
    else:
        print("❌ Ошибка при создании исполняемого файла")
        sys.exit(1)

if __name__ == "__main__":
    main()