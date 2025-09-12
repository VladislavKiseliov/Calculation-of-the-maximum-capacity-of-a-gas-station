from tkinter import filedialog
import pandas as pd
import chardet


class GetFilePatch:
    @staticmethod
    def get_file_patch_csv():
        # Сначала проверяем, выбрал ли пользователь файл
        try:
            file_path = filedialog.askopenfilename(
                title="Выберите файл для загрузки данных котельной",
                filetypes=[
                    ("CSV files", "*.csv"),
                    ("All files", "*.*"),
                ],
            )
            return file_path
        except FileNotFoundError:
            raise

class CheckEncodingFile:
    @staticmethod
    def detect_encoding(file_path):
        """
            Определяет кодировку файла и обрабатывает возможные ошибки.

            :param file_path: Путь к файлу.
            :return: Предполагаемая кодировка файла (строка) или None, если не удалось определить.
            """
        try:
            # Читаем небольшой кусок файла в бинарном режиме
            with open(file_path, 'rb') as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)

                # Возвращаем кодировку или None, если chardet не смог её определить
                return result['encoding']

        except FileNotFoundError:
            # Обработка случая, когда файл не существует
            raise
        except IOError as e:
            # Обработка других ошибок ввода-вывода (например, проблемы с доступом)
            raise
        except Exception as e:
            # Обработка любых других непредвиденных ошибок
            raise





