import configparser
from tkinter import simpledialog

def load_settings():
    config = configparser.ConfigParser()
    with open('AmDB.ini', 'r', encoding='utf-8') as file:
        config.read_file(file)
    return config

def save_settings(username, x=None, y=None, width=None, height=None):
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

def get_username(current_name=""):
    return simpledialog.askstring(
        "Имя пользователя",
        "Введите ваше имя:",
        initialvalue=current_name)