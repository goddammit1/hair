# bot_logic.py

import threading
import logging
import telebot
from telebot import types
from config import TOKEN
from image_handler import get_image_paths, send_image
from jsonreader import FileReader  # Импортируем класс-ридер
from constants import param_types, next_param, step_data, param_dependencies
from logger_setup import setup_logger, get_user_logger  # Импортируем оба логгера

class HairBot:
    def __init__(self, log_queue):
        """
        Инициализирует HairBot и настраивает логирование.
        Args:
            log_queue: очередь из GUI для логов
        """
        # Настраиваем глобальный логгер для бота с передачей очереди
        setup_logger(log_queue)
        # Берём настроенный глобальный логгер
        self.logger = logging.getLogger('bot')

        self.bot = telebot.TeleBot(TOKEN)
        # Загружаем данные причесок через FileReader
        reader = FileReader()
        self.hairstyles_data = reader.read_json('hair.json') or {}
        self.selection_store = {}
        self.thread = None
        self._register_handlers()

    def _register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            chat_id = message.chat.id
            self.selection_store[chat_id] = {}
            options = self.get_options('face', {})
            if not options:
                self.bot.send_message(chat_id, "Ошибка: данные о прическах не найдены!")
                return
            self.send_selection_photo(
                chat_id,
                step_data['face']['image'],
                step_data['face']['caption'],
                options,
                'face'
            )

        @self.bot.callback_query_handler(func=lambda call: True)
        def handle_query(call):
            chat_id = call.message.chat.id
            if chat_id not in self.selection_store:
                self.selection_store[chat_id] = {}
            selection = self.selection_store[chat_id]

            # Определяем выбранный параметр
            for param in param_types:
                if call.data.startswith(param + '_'):
                    param_type = param
                    selected_value = call.data[len(param) + 1:]
                    break
            else:
                self.bot.answer_callback_query(call.id, "Неверный формат данных!")
                return

            # Проверяем зависимость от 'face'
            if param_type != 'face' and 'face' not in selection:
                options = self.get_options('face', {})
                self.send_selection_photo(
                    chat_id,
                    step_data['face']['image'],
                    step_data['face']['caption'],
                    options,
                    'face'
                )
                self.bot.answer_callback_query(call.id)
                return

            # Сохраняем выбор и логируем состояние
            selection[param_type] = selected_value
            get_user_logger(chat_id).info(f"Состояние chat {chat_id}: {selection}")

            # Переходим к следующему шагу
            next_type = next_param.get(param_type)
            if next_type:
                options = self.get_options(next_type, selection)
                if not options:
                    self.bot.send_message(chat_id, f"Ошибка: варианты для {next_type} не найдены!")
                    self.bot.answer_callback_query(call.id)
                    return
                self.send_selection_photo(
                    chat_id,
                    step_data[next_type]['image'],
                    step_data[next_type]['caption'],
                    options,
                    next_type
                )
            else:
                # Финальный результат
                face = selection['face']
                length = selection['hair_length']
                htype = selection['hair_type']
                color = selection['hair_color']
                image_paths = get_image_paths(self.hairstyles_data, face, length, htype, color)
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
        keyboard = types.InlineKeyboardMarkup()
        for opt in options:
            keyboard.add(types.InlineKeyboardButton(text=opt, callback_data=f"{callback_prefix}_{opt}"))
        return keyboard

    def send_selection_photo(self, chat_id, image_path, caption, options, callback_prefix):
        keyboard = self.create_keyboard(options, callback_prefix)
        with open(image_path, 'rb') as img:
            self.bot.send_photo(chat_id, photo=img, caption=caption, reply_markup=keyboard)

    def run(self):
        try:
            self.logger.info("Бот начал работу")
            self.bot.polling(none_stop=True, skip_pending=True, timeout=1)
        except Exception as e:
            self.logger.error(f"Ошибка при запуске бота: {e}")
        finally:
            self.logger.info("Поток бота завершен")

    def start(self):
        if self.thread and self.thread.is_alive():
            return
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.thread.start()

    def stop(self):
        self.bot.stop_polling()