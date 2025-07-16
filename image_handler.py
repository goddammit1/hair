import logging

# Настраиваем логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_image_path(data, face_type, hair_type, hair_color, hair_length):
    
    try:
        # Ищем путь в словаре
        if face_type in data:
            if hair_type in data[face_type]:
                if hair_color in data[face_type][hair_type]:
                    if hair_length in data[face_type][hair_type][hair_color]:
                        return data[face_type][hair_type][hair_color][hair_length]
        
        logger.warning(f"Изображение не найдено для: {face_type}, {hair_type}, {hair_color}, {hair_length}")
        return None
    except Exception as e:
        logger.error(f"Ошибка при получении пути изображения: {e}")
        return None

def send_image(bot, chat_id, image_path):
    """
    Отправляет изображение пользователю через Telegram.

    Args:
        bot: Экземпляр бота Telegram.
        chat_id (int): ID чата пользователя.
        image_path (str): Путь до изображения.

    Returns:
        bool: True, если отправка успешна, False в противном случае.
    """
    try:
        with open(image_path, 'rb') as image_file:
            bot.send_photo(chat_id=chat_id, photo=image_file)
        logger.info(f"Изображение отправлено в чат {chat_id}")
        return True
    except FileNotFoundError:
        logger.error(f"Файл изображения не найден: {image_path}")
        return False
    except Exception as e:
        logger.error(f"Ошибка при отправке изображения: {e}")
        return False