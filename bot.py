import telebot
from telebot import types
from config import TOKEN
from image_handler import get_image_paths, send_image
from jsonreader import read_json
from constants import param_types, next_param, step_data, param_dependencies
from logger_setup import logger 

# Инициализируем бота
bot = telebot.TeleBot(TOKEN)

# Читаем данные из JSON-файла
hairstyles_data = read_json('hair.json')

# Глобальный словарь для хранения состояния
selection_store = {}

# Функция для получения вариантов выбора
def get_options(param_type, selection):
    dependencies = param_dependencies[param_type]
    data = hairstyles_data
    for dep in dependencies:
        if dep not in selection:
            return []
        data = data[selection[dep]]
    return list(data.keys())

# Функция для создания клавиатуры
def create_keyboard(options, callback_prefix):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=f"{callback_prefix}_{option}"))
    return keyboard

# Функция для отправки фото с клавиатурой
def send_selection_photo(chat_id, image_path, caption, options, callback_prefix):
    keyboard = create_keyboard(options, callback_prefix)
    with open(image_path, 'rb') as image_file:
        bot.send_photo(chat_id, photo=image_file, caption=caption, reply_markup=keyboard)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    selection_store[chat_id] = {}
    options = get_options('face', {})
    if not options:
        bot.send_message(chat_id, "Ошибка: данные о прическах не найдены!")
        return
    send_selection_photo(chat_id, step_data['face']['image'], step_data['face']['caption'], options, 'face')

# Обработчик callback-запросов
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if chat_id not in selection_store:
        selection_store[chat_id] = {}
    selection = selection_store[chat_id]
    
    for param in param_types:
        if call.data.startswith(param + '_'):
            param_type = param
            selected_value = call.data[len(param) + 1:]
            break
    else:
        bot.answer_callback_query(call.id, "Неверный формат данных!")
        return
    
    selection[param_type] = selected_value
    logger.info(f"Текущее состояние для chat {chat_id}: {selection}")  
    
    next_param_type = next_param.get(param_type)
    if next_param_type:
        options = get_options(next_param_type, selection)
        if not options:
            bot.send_message(chat_id, f"Ошибка: варианты для {next_param_type} не найдены!")
            bot.answer_callback_query(call.id)
            return
        image_path = step_data[next_param_type]['image']
        caption = step_data[next_param_type]['caption']
        send_selection_photo(chat_id, image_path, caption, options, next_param_type)
    else:
        face_type = selection['face']
        hair_length = selection['hair_length']
        hair_type = selection['hair_type']
        hair_color = selection['hair_color']
        image_paths = get_image_paths(hairstyles_data, face_type, hair_length, hair_type, hair_color)
        if image_paths:
            send_image(bot, chat_id, image_paths)
        else:
            bot.send_message(chat_id, "Извини, такого изображения нет!")
    
    bot.answer_callback_query(call.id)

# Запуск бота
if __name__ == '__main__':
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")  