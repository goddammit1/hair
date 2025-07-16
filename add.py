import json
import os
import tkinter as tk
from tkinter import filedialog, messagebox

# Путь к JSON-файлу
JSON_FILE = "hair.json"

def save_to_json(data):
    """Сохраняет данные в JSON-файл."""
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def load_json():
    """Загружает данные из JSON-файла или возвращает пустой список."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def add_image():
    """Добавляет новую запись в JSON-файл."""
    face_shape = entry_face_shape.get()
    hair_type = entry_hair_type.get()
    hair_color = entry_hair_color.get()
    hair_length = entry_hair_length.get()
    image_path = entry_image_path.get()

    if not all([face_shape, hair_type, hair_color, hair_length, image_path]):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    if not os.path.exists(image_path):
        messagebox.showerror("Ошибка", "Указанный файл не найден!")
        return

    new_entry = {
        "face_shape": face_shape,
        "hair_type": hair_type,
        "hair_color": hair_color,
        "hair_length": hair_length,
        "image_path": image_path
    }

    data = load_json()
    data.append(new_entry)
    save_to_json(data)
    messagebox.showinfo("Успех", "Изображение успешно добавлено!")

def browse_file():
    """Открывает диалог для выбора файла."""
    file_path = filedialog.askopenfilename()
    if file_path:
        entry_image_path.delete(0, tk.END)
        entry_image_path.insert(0, file_path)

# Создание основного окна
root = tk.Tk()
root.title("Добавить изображение")

# Поля ввода
tk.Label(root, text="Форма лица:").grid(row=0, column=0, padx=10, pady=5)
entry_face_shape = tk.Entry(root)
entry_face_shape.grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Тип волос:").grid(row=1, column=0, padx=10, pady=5)
entry_hair_type = tk.Entry(root)
entry_hair_type.grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Цвет волос:").grid(row=2, column=0, padx=10, pady=5)
entry_hair_color = tk.Entry(root)
entry_hair_color.grid(row=2, column=1, padx=10, pady=5)

tk.Label(root, text="Длина волос:").grid(row=3, column=0, padx=10, pady=5)
entry_hair_length = tk.Entry(root)
entry_hair_length.grid(row=3, column=1, padx=10, pady=5)

tk.Label(root, text="Путь к изображению:").grid(row=4, column=0, padx=10, pady=5)
entry_image_path = tk.Entry(root)
entry_image_path.grid(row=4, column=1, padx=10, pady=5)

# Кнопка для выбора файла
btn_browse = tk.Button(root, text="Выбрать файл", command=browse_file)
btn_browse.grid(row=4, column=2, padx=10, pady=5)

# Кнопка для добавления
btn_add = tk.Button(root, text="Добавить", command=add_image)
btn_add.grid(row=5, column=0, columnspan=3, pady=10)

# Запуск основного цикла
root.mainloop()