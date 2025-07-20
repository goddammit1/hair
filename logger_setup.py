import logging
import os
import queue

# Глобальная очередь для логов (будет передана из GUI)
log_queue = None  # Инициализируем как None, значение будет задано из GUI

class QueueHandler(logging.Handler):
    """Обработчик логов, записывающий сообщения в очередь."""
    def __init__(self, log_queue):
        super().__init__()
        self.log_queue = log_queue

    def emit(self, record):
        try:
            msg = self.format(record)
            self.log_queue.put(msg)
        except Exception:
            self.handleError(record)

def setup_logger(log_queue_ref):
    """
    Настраивает глобальный логгер для событий бота.
    Args:
        log_queue_ref: Ссылка на очередь из GUI
    """
    global log_queue
    log_queue = log_queue_ref  # Присваиваем глобальной переменной очередь из GUI

    logger = logging.getLogger('bot')
    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.INFO)

    # Форматтер
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Обработчик для файла bot.log
    file_handler = logging.FileHandler('logs/bot.log', mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Обработчик для очереди
    queue_handler = QueueHandler(log_queue)
    queue_handler.setFormatter(formatter)
    logger.addHandler(queue_handler)

    return logger

# Словарь для хранения пользовательских логгеров
user_loggers = {}

def get_user_logger(chat_id):
    """
    Возвращает или создает логгер для конкретного пользователя.
    Args:
        chat_id: ID чата пользователя
    Returns:
        logging.Logger: Логгер для данного пользователя
    """
    if chat_id in user_loggers:
        return user_loggers[chat_id]

    user_logger = logging.getLogger(f"user_{chat_id}")
    user_logger.setLevel(logging.INFO)

    # Обработчик для файла user_<chat_id>.log
    file_handler = logging.FileHandler(f'logs/user_{chat_id}.log', mode='a')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    # Обработчик для очереди с префиксом [User <chat_id>]
    queue_handler = QueueHandler(log_queue)
    queue_handler.setFormatter(logging.Formatter(f'[User {chat_id}] %(asctime)s - %(levelname)s - %(message)s'))

    # Добавляем обработчики
    user_logger.addHandler(file_handler)
    user_logger.addHandler(queue_handler)

    # Отключаем передачу в глобальный логгер
    user_logger.propagate = False

    user_loggers[chat_id] = user_logger
    return user_logger