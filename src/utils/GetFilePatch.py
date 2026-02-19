from tkinter import filedialog
import pandas as pd
from typing import Optional

try:
    import chardet
except ImportError:
    chardet = None


class GetFilePatch:
    @staticmethod
    def get_file_patch_csv(title:str) ->  Optional[str]:
        # Сначала проверяем, выбрал ли пользователь файл
        try:
            file_path = filedialog.askopenfilename(
                title=title,
                defaultextension=".csv",  # Расширение по умолчанию
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("All files", "*.*"),
                ],
            )
            # Проверяем, выбрал ли пользователь файл
            if not file_path:
                return None
            return file_path

        except FileNotFoundError:
            raise FileNotFoundError("Файл не найден")
        except Exception as e:
            raise Exception(f"Произошла ошибка при выборе файла: {str(e)}")

class CheckEncodingFile:
    @staticmethod
    def detect_encoding(file_path):
        """
            Определяет кодировку файла и обрабатывает возможные ошибки.

            :param file_path: Путь к файлу.
            :return: Предполагаемая кодировка файла (строка) или None, если не удалось определить.
            """
        try:
            # Читаем файл в бинарном режиме
            with open(file_path, "rb") as f:
                raw_data = f.read()

            # Если chardet установлен, используем его
            if chardet is not None:
                result = chardet.detect(raw_data)
                encoding = result.get("encoding")
                if encoding:
                    return encoding

            # Fallback без chardet: простая проверка популярных кодировок
            if raw_data.startswith(b"\xef\xbb\xbf"):
                return "utf-8-sig"

            for candidate in ("utf-8", "cp1251"):
                try:
                    raw_data.decode(candidate)
                    return candidate
                except UnicodeDecodeError:
                    continue

            # Последний безопасный вариант
            return "latin-1"

        except FileNotFoundError:
            # Обработка случая, когда файл не существует
            raise
        except IOError as e:
            # Обработка других ошибок ввода-вывода (например, проблемы с доступом)
            raise
        except Exception as e:
            # Обработка любых других непредвиденных ошибок
            raise





