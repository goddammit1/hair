import telebot
from telebot import types
from config import TOKEN  # Импортируем токен из config.py
from image_handler import get_image_paths, send_image  # Обновили get_image_path на get_image_paths
from jsonreader import read_json

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Читаем данные из JSON-файла
hairstyles_data = read_json('hair.json')

# Функция для получения списка доступных вариантов для параметра
def get_options(param, current_selection=None):
    if param == 'face_type':
        return list(hairstyles_data.keys())
    elif param == 'hair_type' and current_selection and 'face' in current_selection:
        face_type = current_selection['face']
        print(f"Attempting to access hairstyles_data['{face_type}']")
        return list(hairstyles_data[current_selection['face']].keys())
    elif param == 'hair_color' and current_selection and 'hair_type' in current_selection:
        return list(hairstyles_data[current_selection['face']][current_selection['hair_type']].keys())
    elif param == 'hair_length' and current_selection and 'hair_color' in current_selection:
        return list(hairstyles_data[current_selection['face']][current_selection['hair_type']][current_selection['hair_color']].keys())
    return []

# Функция для создания клавиатуры с кнопками
def create_keyboard(options, callback_prefix):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=f"{callback_prefix}_{option}"))
    return keyboard

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    face_types = get_options('face_type')
    if not face_types:
        bot.send_message(message.chat.id, "Ошибка: данные о прическах не найдены!")
        return
    keyboard = create_keyboard(face_types, 'face')
    bot.send_message(message.chat.id, "Выберите тип лица:", reply_markup=keyboard)

known_param_types = ['face', 'hair_type', 'hair_color', 'hair_length']

# Создаем глобальный словарь для хранения состояния выбора
selection_store = {}

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    # Уникальный ключ для сообщения: (chat_id, message_id)
    key = (call.message.chat.id, call.message.message_id)
    
    # Инициализируем selection для этого сообщения, если его нет
    if key not in selection_store:
        selection_store[key] = {}
    selection = selection_store[key]
    
    # Проверяем, с какого известного param_type начинается callback_data
    for param in known_param_types:
        if call.data.startswith(param + '_'):
            param_type = param
            selected_value = call.data[len(param) + 1:]
            break
    else:
        bot.answer_callback_query(call.id, "Неверный формат данных!")
        return
    
    # Обновляем selection с новым параметром
    selection[param_type] = selected_value
    print(f"Current selection: {selection}")
    
    # Логика для каждого шага
    if param_type == 'face':
        hair_types = get_options('hair_type', selection)
        if not hair_types:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                 text="Ошибка: типы волос не найдены!")
            return
        keyboard = create_keyboard(hair_types, 'hair_type')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             text="Выберите тип волос:", reply_markup=keyboard)
    
    elif param_type == 'hair_type':
        hair_colors = get_options('hair_color', selection)
        if not hair_colors:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                 text="Ошибка: цвета волос не найдены!")
            return
        keyboard = create_keyboard(hair_colors, 'hair_color')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             text="Выберите цвет волос:", reply_markup=keyboard)
    
    elif param_type == 'hair_color':
        hair_lengths = get_options('hair_length', selection)
        if not hair_lengths:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                 text="Ошибка: длины волос не найдены!")
            return
        keyboard = create_keyboard(hair_lengths, 'hair_length')
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                             text="Выберите длину волос:", reply_markup=keyboard)
    
    elif param_type == 'hair_length':
        # Все параметры выбраны, отправляем изображения
        face_type = selection['face']
        hair_type = selection['hair_type']
        hair_color = selection['hair_color']
        hair_length = selected_value
        
        image_paths = get_image_paths(hairstyles_data, face_type, hair_type, hair_color, hair_length)
        if image_paths:
            send_image(bot, call.message.chat.id, image_paths)
            bot.delete_message(call.message.chat.id, call.message.message_id)
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, 
                                 text="Извини, такого изображения нет!")

# Запускаем бота
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")