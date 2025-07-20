import json
import logging  # Заменяем импорт

class FileReader:
    def __init__(self):
        self.logger = logging.getLogger('bot')  # Используем уже настроенный логгер

    def read_json(self, file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as json_file:
                data = json.load(json_file)
            self.logger.info(f"JSON-файл {file_path} успешно загружен.")
            return data
        except FileNotFoundError:
            self.logger.error(f"Файл {file_path} не найден.")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(f"Ошибка при чтении JSON-файла: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Неизвестная ошибка при чтении JSON-файла: {e}")
            return None