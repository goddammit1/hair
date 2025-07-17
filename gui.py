# gui.py

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
        self.configure(fg_color="#000000")

        # Загрузка пользовательского фонового изображения
        bg_pil_image = Image.open("assets/Group_5.jpg")
        self.bg_ctk_image = ctk.CTkImage(bg_pil_image, size=(960, 540))
        self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image)
        self.bg_label.place(x=0, y=0)
        self.bg_label.lower()

        # Привязка событий для перетаскивания
        self.bg_label.bind("<ButtonPress-1>", self.start_move)
        self.bg_label.bind("<B1-Motion>", self.do_move)
        
        log_font = ctk.CTkFont(family="IBM Plex Sans Thai Looped", size=11)


        # Start and Stop buttons (bottom area)
        self.start_button = ctk.CTkButton(
            self,
            text="Start Bot",
            width=120, height=40,
            fg_color="black",
            hover_color="gray",
            text_color="white",
            font=log_font,
            command=self.start_bot
        )
        self.start_button.place(relx=0.25, rely=0.92, anchor="center")

        self.stop_button = ctk.CTkButton(
            self,
            text="Stop Bot",
            width=120, height=40,
            fg_color="black",
            hover_color="gray",
            text_color="white",
            font=log_font,
            command=self.stop_bot
        )
        self.stop_button.place(relx=0.75, rely=0.92, anchor="center")
        self.stop_button.configure(state="disabled")

        
        self.textbox = ctk.CTkTextbox(
            self, width=560, height=300, corner_radius=10,
            fg_color="transparent", text_color="white",
            border_width=1, border_color="#333333",
            font=log_font
        )
        self.textbox.place(relx=0.5, rely=0.5, anchor="center")
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
        
      
        
        
    def _add_to_taskbar(self):
        """
        На Windows: добавляем WS_EX_APPWINDOW и убираем WS_EX_TOOLWINDOW,
        чтобы окно с overrideredirect всё равно показывалось в таскбаре.
        """
        hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
        # флаг расширенного стиля
        GWL_EXSTYLE = -20
        WS_EX_APPWINDOW  = 0x00040000
        WS_EX_TOOLWINDOW = 0x00000080

        # читаем текущие стили
        ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
        # добавляем APPWINDOW, убираем TOOLWINDOW
        ex_style = (ex_style | WS_EX_APPWINDOW) & ~WS_EX_TOOLWINDOW
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)

        # нужно пересчитать Z-order, иначе не всегда вступает в силу
        SWP_NOSIZE   = 0x0001
        SWP_NOMOVE   = 0x0002
        SWP_NOZORDER = 0x0004
        SWP_FRAMECHANGED = 0x0020
        ctypes.windll.user32.SetWindowPos(hwnd, 0, 0, 0, 0, 0,
                                          SWP_NOSIZE|SWP_NOMOVE|SWP_NOZORDER|SWP_FRAMECHANGED)
        
    def create_background_image(self, width, height):
        """
        Create a gradient background image with colored circles.
        """
        # Vertical gradient base (purple to black)
        base = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        color_top = (50, 0, 150)   # purpleish top color
        color_bottom = (0, 0, 0)   # black bottom
        for y in range(height):
            ratio = y / (height - 1)
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            for x in range(width):
                base.putpixel((x, y), (r, g, b, 255))
        # Overlay semi-transparent neon circles
        overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        circles = [
            (150, 350, 150, (200, 0, 255, 120)),   # purple circle
            (80, 80, 70, (255, 100, 200, 100)),    # pink circle
            (550, 50, 80, (0, 255, 200, 100)),     # teal circle
            (500, 350, 100, (100, 50, 255, 100))   # blue circle
        ]
        for (cx, cy, r, color) in circles:
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)
        # Composite overlay on base
        bg = Image.alpha_composite(base, overlay)
        return bg
        
    def start_move(self, event):
        """Record starting mouse position for dragging."""
        self._drag_start_x = event.x
        self._drag_start_y = event.y

    def do_move(self, event):
        """Handle the window movement."""
        x = self.winfo_pointerx() - self._drag_start_x
        y = self.winfo_pointery() - self._drag_start_y
        self.geometry(f'+{x}+{y}')

    def start_bot(self):
        """
        Обработчик нажатия кнопки «Запустить бота».
        """
        if self.bot_logic.thread and self.bot_logic.thread.is_alive():
            return
        logger.info("Запуск бота...")
        self.bot_logic.start()
        # заменено .config на .configure
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")

    def stop_bot(self):
        """
        Обработчик нажатия кнопки «Остановить бота».
        """
        logger.info("Остановка бота...")
        self.bot_logic.stop()
        # заменено .config на .configure
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")

    def update_logs(self):
        """
        Переносит сообщения из очереди логов в виджет Textbox.
        """
        while not self.log_queue.empty():
            message = self.log_queue.get()
            # заменено self.log_text на self.textbox
            self.textbox.configure(state="normal")
            self.textbox.insert(tk.END, message + '\n')
            self.textbox.see(tk.END)
            self.textbox.configure(state="disabled")
        self.after(100, self.update_logs)

    def on_closing(self):
        """
        Обработчик закрытия окна с безопасной остановкой бота.
        """
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
