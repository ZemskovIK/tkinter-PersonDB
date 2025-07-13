import configparser
from tkinter import simpledialog
from typing import Optional

def load_settings() -> configparser.ConfigParser:
    config = configparser.ConfigParser()
    with open('AmDB.ini', 'r', encoding='utf-8') as file:
        config.read_file(file)
    return config

def save_settings(
    username: str,
    x: Optional[int] = None,
    y: Optional[int] = None,
    width: Optional[int] = None,
    height: Optional[int] = None
) -> None:
    config = configparser.ConfigParser()
    config['main'] = {
    'username': username or 'Гость',
    'top': str(y),
    'left': str(x),
    'width': str(width),
    'height': str(height)
    }
    with open('AmDB.ini', 'w', encoding="utf-8") as file:
        config.write(file)

def get_username(current_name: str = "") -> Optional[str]:
    return simpledialog.askstring(
        "Имя пользователя",
        "Введите ваше имя:",
        initialvalue=current_name)