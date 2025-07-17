import telebot
from telebot import types
from config import TOKEN  # Импортируем токен из config.py
from image_handler import get_image_paths, send_image
from jsonreader import read_json

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Читаем данные из JSON-файла
hairstyles_data = read_json('hair.json')

# Функция для получения списка доступных вариантов для параметра
def get_options(param, current_selection=None):
    if param == 'face_type':
        return list(hairstyles_data.keys())
    elif param == 'hair_length' and current_selection and 'face' in current_selection:
        return list(hairstyles_data[current_selection['face']].keys())
    elif param == 'hair_type' and current_selection and 'hair_length' in current_selection:
        return list(hairstyles_data[current_selection['face']][current_selection['hair_length']].keys())
    elif param == 'hair_color' and current_selection and 'hair_type' in current_selection:
        return list(hairstyles_data[current_selection['face']][current_selection['hair_length']][current_selection['hair_type']].keys())
    return []

# Функция для создания клавиатуры с кнопками
def create_keyboard(options, callback_prefix):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=f"{callback_prefix}_{option}"))
    return keyboard

# Глобальный словарь для хранения состояния выбора по chat_id
selection_store = {}  # chat_id -> selection_dict

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    selection_store[chat_id] = {}  # Сбрасываем состояние выбора
    face_types = get_options('face_type')
    if not face_types:
        bot.send_message(chat_id, "Ошибка: данные о прическах не найдены!")
        return
    keyboard = create_keyboard(face_types, 'face')
    with open('assets/1.jpg', 'rb') as image_file:
        bot.send_photo(chat_id, photo=image_file, caption="Выберите форму лица:", reply_markup=keyboard)

known_param_types = ['face', 'hair_length', 'hair_type', 'hair_color']

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    # Инициализируем состояние для chat_id, если его нет
    if chat_id not in selection_store:
        selection_store[chat_id] = {}
    selection = selection_store[chat_id]
    
    # Парсим данные callback
    for param in known_param_types:
        if call.data.startswith(param + '_'):
            param_type = param
            selected_value = call.data[len(param) + 1:]
            break
    else:
        bot.answer_callback_query(call.id, "Неверный формат данных!")
        return
    
    # Обновляем состояние выбора
    selection[param_type] = selected_value
    print(f"Текущее состояние для chat {chat_id}: {selection}")
    
    # Логика для каждого шага
    if param_type == 'face':
        hair_lengths = get_options('hair_length', selection)
        if not hair_lengths:
            bot.send_message(chat_id, "Ошибка: длины волос не найдены!")
            return
        keyboard = create_keyboard(hair_lengths, 'hair_length')
        with open('assets/2.jpg', 'rb') as image_file:
            bot.send_photo(chat_id, photo=image_file, caption="Выберите длину волос:", reply_markup=keyboard)
    
    elif param_type == 'hair_length':
        hair_types = get_options('hair_type', selection)
        if not hair_types:
            bot.send_message(chat_id, "Ошибка: типы волос не найдены!")
            return
        keyboard = create_keyboard(hair_types, 'hair_type')
        with open('assets/3.jpg', 'rb') as image_file:
            bot.send_photo(chat_id, photo=image_file, caption="Выберите тип волос:", reply_markup=keyboard)
    
    elif param_type == 'hair_type':
        hair_colors = get_options('hair_color', selection)
        if not hair_colors:
            bot.send_message(chat_id, "Ошибка: цвета волос не найдены!")
            return
        keyboard = create_keyboard(hair_colors, 'hair_color')
        with open('assets/4.jpg', 'rb') as image_file:
            bot.send_photo(chat_id, photo=image_file, caption="Выберите цвет волос:", reply_markup=keyboard)
    
    elif param_type == 'hair_color':
        # Все параметры выбраны, отправляем изображения
        face_type = selection['face']
        hair_length = selection['hair_length']
        hair_type = selection['hair_type']
        hair_color = selected_value
        image_paths = get_image_paths(hairstyles_data, face_type, hair_length, hair_type, hair_color)
        if image_paths:
            send_image(bot, chat_id, image_paths)
            # Опционально: удаляем предыдущее сообщение
            # bot.delete_message(chat_id, call.message.message_id)
        else:
            bot.send_message(chat_id, "Извини, такого изображения нет!")

# Запускаем бота
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")