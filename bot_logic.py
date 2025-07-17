# bot_logic.py

import threading
import telebot
from telebot import types
from config import TOKEN
from image_handler import get_image_paths, send_image
from jsonreader import read_json
from constants import param_types, next_param, step_data, param_dependencies
from logger_setup import logger

class HairBot:
    def __init__(self):
        self.bot = telebot.TeleBot(TOKEN)
        self.hairstyles_data = read_json('hair.json')  # данные о прическах
        self.selection_store = {}  # словарь для хранения выбора пользователя по chat_id
        self.thread = None
        self._register_handlers()

    def _register_handlers(self):
        # Обработчик команды /start
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            chat_id = message.chat.id
            self.selection_store[chat_id] = {}
            options = self.get_options('face', {})
            if not options:
                self.bot.send_message(chat_id, "Ошибка: данные о прическах не найдены!")
                return
            # Отправляем фото с вариантом выбора лица
            self.send_selection_photo(chat_id,
                                      step_data['face']['image'],
                                      step_data['face']['caption'],
                                      options, 'face')

        # Обработчик callback-запросов от Inline-кнопок
        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            chat_id = call.message.chat.id
            if chat_id not in self.selection_store:
                self.selection_store[chat_id] = {}
            selection = self.selection_store[chat_id]

            # Определяем, какой параметр выбран из callback_data
            for param in param_types:
                if call.data.startswith(param + '_'):
                    param_type = param
                    selected_value = call.data[len(param) + 1:]
                    break
            else:
                self.bot.answer_callback_query(call.id, "Неверный формат данных!")
                return

            # Если выбран не «face», но лицо ещё не было выбрано — сбрасываем к первому шагу
            if param_type != 'face' and 'face' not in selection:
                options = self.get_options('face', {})
                self.send_selection_photo(chat_id,
                                          step_data['face']['image'],
                                          step_data['face']['caption'],
                                          options, 'face')
                self.bot.answer_callback_query(call.id)
                return

            # Сохраняем выбор
            selection[param_type] = selected_value
            logger.info(f"Текущее состояние для chat {chat_id}: {selection}")

            # Переходим к следующему параметру
            next_param_type = next_param.get(param_type)
            if next_param_type:
                options = self.get_options(next_param_type, selection)
                if not options:
                    self.bot.send_message(chat_id, f"Ошибка: варианты для {next_param_type} не найдены!")
                    self.bot.answer_callback_query(call.id)
                    return
                image_path = step_data[next_param_type]['image']
                caption = step_data[next_param_type]['caption']
                self.send_selection_photo(chat_id, image_path, caption, options, next_param_type)
            else:
                # Финальный этап: формируем результат по всем параметрам
                face_type = selection['face']
                hair_length = selection['hair_length']
                hair_type = selection['hair_type']
                hair_color = selection['hair_color']
                image_paths = get_image_paths(self.hairstyles_data,
                                              face_type, hair_length, hair_type, hair_color)
                if image_paths:
                    send_image(self.bot, chat_id, image_paths)
                else:
                    self.bot.send_message(chat_id, "Извини, такого изображения нет!")
            self.bot.answer_callback_query(call.id)

    def get_options(self, param_type, selection):
        """
        Возвращает список опций для заданного параметра с учётом зависимостей.
        """
        dependencies = param_dependencies[param_type]
        data = self.hairstyles_data
        for dep in dependencies:
            if dep not in selection:
                return []
            data = data[selection[dep]]
        return list(data.keys())

    def create_keyboard(self, options, callback_prefix):
        """
        Создаёт InlineKeyboardMarkup из списка опций.
        """
        keyboard = types.InlineKeyboardMarkup()
        for opt in options:
            keyboard.add(types.InlineKeyboardButton(text=opt, callback_data=f"{callback_prefix}_{opt}"))
        return keyboard

    def send_selection_photo(self, chat_id, image_path, caption, options, callback_prefix):
        """
        Отправляет фото с подписью и встроенной клавиатурой опций.
        """
        keyboard = self.create_keyboard(options, callback_prefix)
        with open(image_path, 'rb') as img:
            self.bot.send_photo(chat_id, photo=img, caption=caption, reply_markup=keyboard)

    def run(self):
        """
        Основной цикл бота (polling). Запускается в отдельном потоке.
        """
        try:
            logger.info("Бот начал работу")
            self.bot.polling(none_stop=True, skip_pending=True, timeout=1)
        except Exception as e:
            logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            logger.info("Поток бота завершен")

    def start(self):
        """
        Запускает бота в отдельном потоке.
        """
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        """
        Останавливает бота.
        """
        self.bot.stop_polling()
