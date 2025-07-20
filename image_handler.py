import logging  # Добавляем импорт

def get_image_paths(data, face_type, hair_type, hair_color, hair_length):
    paths = data.get(face_type, {}).get(hair_type, {}).get(hair_color, {}).get(hair_length, [])
    if not paths:
        logging.getLogger('bot').warning(f"Изображения не найдены для: {face_type}, {hair_type}, {hair_color}, {hair_length}")
    return paths

def send_image(bot, chat_id, image_path):
    if isinstance(image_path, str):
        try:
            with open(image_path, 'rb') as image_file:
                bot.send_photo(chat_id=chat_id, photo=image_file)
            logging.getLogger('bot').info(f"Изображение отправлено в чат {chat_id}: {image_path}")
            return True
        except FileNotFoundError:
            logging.getLogger('bot').error(f"Файл изображения не найден: {image_path}")
            return False
        except Exception as e:
            logging.getLogger('bot').error(f"Ошибка при отправке изображения {image_path}: {e}")
            return False
    elif isinstance(image_path, list):
        success = True
        for path in image_path:
            if not send_image(bot, chat_id, path):
                success = False
        return success
    else:
        logging.getLogger('bot').error(f"Неверный тип image_path: {type(image_path)}")
        return False