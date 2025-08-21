import sys
import platform

def detect_python():
    """Определяет тип и версию Python"""
    
    print("=== ИНФОРМАЦИЯ О PYTHON ===")
    
    # Версия
    print(f"Версия: {sys.version}")
    
    # Реализация
    impl = platform.python_implementation()
    print(f"Реализация: {impl}")
    
    # Путь
    print(f"Путь: {sys.executable}")
    
    # Платформа
    print(f"Платформа: {sys.platform}")
    
    # Специфичные признаки
    if hasattr(sys, 'pypy_version_info'):
        print("🔥 Это PyPy!")
    elif sys.platform.startswith('java'):
        print("☕ Это Jython!")
    elif sys.platform.startswith('cli'):
        print("🔷 Это IronPython!")
    else:
        print("🐍 Это CPython (стандартный Python)")

# Запуск
detect_python()