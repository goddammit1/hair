import json
import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def read_json(file_path):
    """
    Читает JSON-файл и возвращает его содержимое в виде словаря.

    Args:
        file_path (str): Путь до JSON-файла.

    Returns:
        dict: Содержимое JSON-файла или None, если файл не найден или возникла ошибка.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as json_file:
            data = json.load(json_file)
        logger.info(f"JSON-файл {file_path} успешно загружен.")
        return data
    except FileNotFoundError:
        logger.error(f"Файл {file_path} не найден.")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка при чтении JSON-файла: {e}")
        return None
    except Exception as e:
        logger.error(f"Неизвестная ошибка при чтении JSON-файла: {e}")
        return None