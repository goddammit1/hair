import sys
import queue
import logging
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QMessageBox
)
from PyQt6.QtGui import QPixmap, QFont, QResizeEvent, QCloseEvent, QMouseEvent
from PyQt6.QtCore import QTimer, Qt, QPoint
from bot_logic import HairBot
from logger_setup import setup_logger
import ctypes

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

class BotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HairBot GUI")
        self.setGeometry(100, 100, 960, 540)
        self.setMinimumSize(480, 270)
        self.setStyleSheet("background-color: #000000;")

        # Фоновое изображение
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(0, 0, 960, 540)
        self.bg_label.setScaledContents(True)
        self.load_background_image()

        # Шрифт
        self.log_font = QFont("IBM Plex Sans Thai Looped", 9)

        button_style = """
        QPushButton {
            background-color: black;
            color: white;
            border: none;
            outline: none;
        }
        QPushButton:hover {
            background-color: gray;
        }
        QPushButton:focus {
            outline: none;
        }
        """

        self.start_button = QPushButton("Start Bot", self)
        self.start_button.setGeometry(240, 500, 100, 30)
        self.start_button.setStyleSheet(button_style)
        self.start_button.setFont(self.log_font)
        self.start_button.clicked.connect(self.start_bot)

        self.stop_button = QPushButton("Stop Bot", self)
        self.stop_button.setGeometry(720, 500, 100, 30)
        self.stop_button.setStyleSheet(button_style)
        self.stop_button.setFont(self.log_font)
        self.stop_button.clicked.connect(self.stop_bot)
        self.stop_button.setEnabled(False)

        # Текстовое поле для логов
        self.textbox = QTextEdit(self)
        self.textbox.setGeometry(240, 135, 480, 270)
        self.textbox.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.7);
            color: white;
            border: 1px solid #333333;
            border-radius: 30px;
            padding-left: 20px;    /* отступ слева */
            padding-top: 8px;      /* отступ сверху, по желанию */
            padding-right: 8px;    /* отступ справа */
            padding-bottom: 8px;   /* отступ снизу */
        """)
        self.textbox.setFont(self.log_font)
        self.textbox.setReadOnly(True)

        # Очередь для логов и её обработчик
        self.log_queue = queue.Queue()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setFormatter(formatter)

        # Настраиваем глобальный логгер, передавая очередь
        self.logger = setup_logger(self.log_queue)  # Передаем очередь в setup_logger

        # Модель бота
        self.bot_logic = HairBot(self.log_queue)

        # Timer для обновления логов
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(100)

        # Перетаскивание окна
        self._drag_start_pos = None

    def load_background_image(self):
        pixmap = QPixmap("assets/Group_5.jpg")
        self.bg_label.setPixmap(pixmap)

    def resizeEvent(self, event: QResizeEvent):
        # Обновляем фоновое изображение
        self.bg_label.setGeometry(0, 0, self.width(), self.height())
    
        # Вычисляем коэффициент масштабирования
        scaling_factor = self.height() / 540
    
        # Обновляем размер шрифта
        new_font_size = int(9 * scaling_factor)
        self.log_font.setPointSize(new_font_size)
        self.start_button.setFont(self.log_font)
        self.stop_button.setFont(self.log_font)
        self.textbox.setFont(self.log_font)
        
        # Масштабируем размеры кнопок
        w = int(100 * scaling_factor)  # Новая ширина
        h = int(30 * scaling_factor)   # Новая высота
        
        # Вычисляем позиции кнопок
        x_start = int(self.width() * 0.25 - w / 2)
        x_stop = int(self.width() * 0.75 - w / 2)
        y = int(self.height() * 0.92)
        
        # Обновляем геометрию кнопок
        self.start_button.setGeometry(x_start, y, w, h)
        self.stop_button.setGeometry(x_stop, y, w, h)
        
        # Обновляем геометрию текстового поля
        self.textbox.setGeometry(int(self.width() * 0.25), int(self.height() * 0.25), int(self.width() * 0.5), int(self.height() * 0.5))

    def start_bot(self):
        if self.bot_logic.thread and self.bot_logic.thread.is_alive():
            return
        self.logger.info("Запуск бота...")
        self.bot_logic.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_bot(self):
        self.logger.info("Остановка бота...")
        self.bot_logic.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_logs(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.textbox.append(message)
            self.textbox.ensureCursorVisible()
        # Проверка состояния потока бота
        if self.bot_logic.thread and not self.bot_logic.thread.is_alive() and self.stop_button.isEnabled():
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.logger.info("Бот неожиданно завершился.")

    def closeEvent(self, event: QCloseEvent):
        if self.bot_logic.thread and self.bot_logic.thread.is_alive():
            msgBox = QMessageBox(self)
            msgBox.setWindowTitle("Подтверждение закрытия")
            msgBox.setText("Бот всё ещё работает! Вы уверены, что хотите выйти?")
            msgBox.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            msgBox.setDefaultButton(QMessageBox.StandardButton.No)
            msgBox.setStyleSheet("color: white; background-color: black;")
            reply = msgBox.exec()
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
            self.logger.info("Останавливаем бота...")
            self.bot_logic.stop()
            self.bot_logic.thread.join(timeout=3.0)
            if self.bot_logic.thread.is_alive():
                self.logger.warning("Поток не завершился вовремя!")
        self.logger.info("Приложение закрыто")
        event.accept()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event: QMouseEvent):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_start_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_start_pos)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = None

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")  # Темная тема
    window = BotGUI()
    window.show()
    sys.exit(app.exec())
