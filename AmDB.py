from tkinter import Tk, messagebox
from typing import Optional
import settings, database, data, gui, dialogs

def on_close(event: Optional[object] = None) -> None:
    global username
    username = gui.get_current_username()
    settings.save_settings(username, root.winfo_x(),
                root.winfo_y(), root.winfo_width(), 
                root.winfo_height()
                )
    root.destroy()
    
database.create_database()
data.load_initial_data()

config = settings.load_settings()
username = config.get('main', 'username', fallback='Гость')
width = config.getint('main', 'width')
height = config.getint('main', 'height')
x = config.getint('main', 'left')
y = config.getint('main', 'top')

if not username or username == "Гость":
    username = settings.get_username()
    if not username:
        username = "Гость"
    settings.save_settings(username, x, y, width, height)
    
root = Tk()
root.title("Известные исторические личности России")
root.geometry(f"{width}x{height}+{x}+{y}")
root.iconbitmap(default="./icon.ico")
root.protocol("WM_DELETE_WINDOW", on_close)

counter: int = 0
def show_welcome(event: Optional[object] = None) -> None:
    global counter
    global root
    if counter == 0:
        counter += 1
        messagebox.showinfo(title="Добро пожаловать", 
                       message=f"Здравствуйте, {username}!\n"
                       "Добро пожаловать в Фонд AmDB")
        root.unbind("<Visibility>")
        gui.get_listbox().focus_set()

gui.create_gui(root, username)

root.bind("<F1>", dialogs.show_help)
root.bind("<F2>", lambda e: gui.add_person(root))
root.bind("<F3>", gui.delete_person)
root.bind("<F4>", lambda e: gui.edit_person(root))
root.bind("<Control-x>", on_close)
root.bind("<Visibility>", show_welcome)

root.mainloop()