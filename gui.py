import tkinter as tk
from tkinter import scrolledtext, messagebox
import queue
import logging
from bot_logic import HairBot
from logger_setup import logger
import customtkinter as ctk
from PIL import Image, ImageDraw
import ctypes
import pywinstyles

ctk.set_appearance_mode("dark")  # Dark mode
ctk.set_default_color_theme("dark-blue")  # Blue accent theme

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

class BotGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("960x540")
        self.minsize(480, 270)  # Устанавливаем минимальный размер
        self.configure(fg_color="#000000")

        # Загрузка пользовательского фонового изображения
        self.bg_pil_image = Image.open("assets/Group_5.jpg")
        self.bg_ctk_image = ctk.CTkImage(self.bg_pil_image, size=(960, 540))
        self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image)
        self.bg_label.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.bg_label.lower()

        
        self.log_font = ctk.CTkFont(family="IBM Plex Sans Thai Looped", size=11)

        # Start and Stop buttons (bottom area)
        self.start_button = ctk.CTkButton(
            self,
            text="Start Bot",
            fg_color="black",
            hover_color="gray",
            text_color="white",
            font=self.log_font,
            command=self.start_bot
        )
        self.start_button.place(relx=0.25, rely=0.92, anchor="center")

        self.stop_button = ctk.CTkButton(
            self,
            text="Stop Bot",
            fg_color="black",
            hover_color="gray",
            text_color="white",
            font=self.log_font,
            command=self.stop_bot
        )
        self.stop_button.place(relx=0.75, rely=0.92, anchor="center")
        self.stop_button.configure(state="disabled")

        self.textbox = ctk.CTkTextbox(
            self, corner_radius=10,
            fg_color="transparent", text_color="white",
            border_width=1, border_color="#333333",
            font=self.log_font
        )
        self.textbox.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.56, relheight=0.6)
        self.textbox.configure(state="disabled")
        pywinstyles.set_opacity(self.textbox, value=0.9)

        # Очередь для логов и её обработчик
        self.log_queue = queue.Queue()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.queue_handler = QueueHandler(self.log_queue)
        self.queue_handler.setFormatter(formatter)
        logger.addHandler(self.queue_handler)

        # Модель бота
        self.bot_logic = HairBot()

        # Запуск обновления лога каждые 100 мс
        self.after(100, self.update_logs)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        #Уебан открыл окно на весь экран
        self.bind("<Configure>", self.on_resize)

    def on_resize(self, event):
        new_width = self.winfo_width()
        new_height = self.winfo_height()
        # Обновляем фоновое изображение
        self.bg_ctk_image = ctk.CTkImage(self.bg_pil_image, size=(new_width, new_height))
        self.bg_label.configure(image=self.bg_ctk_image)
        # Обновляем размер шрифта
        new_font_size = int(11 * (new_height / 540))
        self.log_font.configure(size=new_font_size)

    def start_move(self, event):
        """Record starting mouse position for dragging."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y


    def start_bot(self):
        if self.bot_logic.thread and self.bot_logic.thread.is_alive():
            return
        logger.info("Запуск бота...")
        self.bot_logic.start()
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_bot(self):
        logger.info("Остановка бота...")
        self.bot_logic.stop()
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def update_logs(self):
        while not self.log_queue.empty():
            message = self.log_queue.get()
            self.textbox.configure(state="normal")
            self.textbox.insert(tk.END, message + '\n')
            self.textbox.see(tk.END)
            self.textbox.configure(state="disabled")
        self.after(100, self.update_logs)

    def on_closing(self):
        if self.bot_logic.thread and self.bot_logic.thread.is_alive():
            confirm = messagebox.askyesno(
                "Подтверждение закрытия",
                "Бот все еще работает! Вы уверены, что хотите выйти?",
                icon='warning'
            )
            if not confirm:
                return
            logger.info("Останавливаем бота...")
            self.bot_logic.stop()
            self.bot_logic.thread.join(timeout=3.0)
            if self.bot_logic.thread.is_alive():
                logger.warning("Поток не завершился вовремя!")
        logger.info("Приложение закрыто")
        self.destroy()

if __name__ == "__main__":
    app = BotGUI()
    app.mainloop()