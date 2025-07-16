import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_image_paths(data, face_type, hair_type, hair_color, hair_length):
    """
    Получает список путей к изображениям по заданным параметрам.
    
    Args:
        data (dict): Словарь с данными изображений.
        face_type (str): Тип лица.
        hair_type (str): Тип волос.
        hair_color (str): Цвет волос.
        hair_length (str): Длина волос.
    
    Returns:
        list: Список путей к изображениям или пустой список, если ничего не найдено.
    """
    paths = data.get(face_type, {}).get(hair_type, {}).get(hair_color, {}).get(hair_length, [])
    if not paths:
        logger.warning(f"Изображения не найдены для: {face_type}, {hair_type}, {hair_color}, {hair_length}")
    return paths

def send_image(bot, chat_id, image_path):
    """
    Отправляет одно или несколько изображений в чат Telegram.
    
    Args:
        bot: Экземпляр бота Telegram.
        chat_id (int): ID чата пользователя.
        image_path (str or list): Путь к изображению или список путей.
    
    Returns:
        bool: True, если все изображения отправлены успешно, False в противном случае.
    """
    if isinstance(image_path, str):
        try:
            with open(image_path, 'rb') as image_file:
                bot.send_photo(chat_id=chat_id, photo=image_file)
            logger.info(f"Изображение отправлено в чат {chat_id}: {image_path}")
            return True
        except FileNotFoundError:
            logger.error(f"Файл изображения не найден: {image_path}")
            return False
        except Exception as e:
            logger.error(f"Ошибка при отправке изображения {image_path}: {e}")
            return False
    elif isinstance(image_path, list):
        success = True
        for path in image_path:
            if not send_image(bot, chat_id, path):
                success = False
        return success
    else:
        logger.error(f"Неверный тип image_path: {type(image_path)}")
        return False