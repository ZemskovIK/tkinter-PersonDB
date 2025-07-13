from tkinter import *
from tkinter import messagebox, simpledialog, filedialog
import dialogs, settings, database, sqlite3
from typing import Optional

DEFAULT_PHOTO_PATH = "./images/noimage.png"
DB_NAME = 'AmDB.db'
IMAGE_SUBSAMPLE = 2

app_state = {
    'current_username': None,
    'persons': [],
    'default_photo': None
}

gui_components = {
    'user_label': None,
    'photo_label': None,
    'bio_text': None,
    'listbox': None,
    'main_menu': None,
    'fond_menu': None
}

def init_default_photo():
    app_state['default_photo'] = PhotoImage(file=DEFAULT_PHOTO_PATH).subsample(IMAGE_SUBSAMPLE)

def get_current_username() -> Optional[str]:
    return app_state['current_username']

def change_user() -> None:
    new_name = settings.get_username(app_state['current_username'])
    if new_name:
        app_state['current_username'] = new_name
        gui_components['user_label'].config(text=f"Пользователь: {new_name}")
        settings.save_settings(new_name)
        messagebox.showinfo("Успешно", f"Имя пользователя изменено на {new_name}")

def refresh_persons_list() -> None:
    app_state['persons'] = database.get_all_persons()
    listbox = gui_components['listbox']
    listbox.delete(0, END)
    
    for person in app_state['persons']:
        listbox.insert(END, person[1])

def find_person() -> None:
    query = simpledialog.askstring("Поиск", "Введите имя для поиска:")
    if not query:
        return
        
    listbox = gui_components['listbox']
    
    for i, person in enumerate(app_state['persons']):
        if query.lower() in person[1].lower():
            listbox.selection_clear(0, END)
            listbox.selection_set(i)
            listbox.see(i)
            listbox.event_generate("<<ListboxSelect>>")
            return
    
    messagebox.showinfo("Поиск", "Ничего не найдено")

def clean_bio_text(text: str) -> str:
    return ' '.join(line.strip() for line in text.split('\n'))

def load_image(filepath: str) -> Optional[bytes]:
    try:
        with open(filepath, 'rb') as file:
            return file.read()
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось загрузить фото: {e}")
        return None

def add_person(root: Tk, event=None) -> None:
    name = simpledialog.askstring("Добавить", "Введите имя:", parent=root)
    if not name:
        get_listbox().focus_set()
        return 
        
    bio = simpledialog.askstring("Добавить", "Введите биографию:", parent=root) or ""
    filepath = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
    img_data = load_image(filepath) if filepath else None
    
    try:
        with sqlite3.connect('AmDB.db') as connection:
            cursor = connection.cursor()
            if img_data:
                cursor.execute('INSERT INTO persons (name, bio, photo) VALUES (?, ?, ?)', 
                            (name, bio, img_data))
            else:
                cursor.execute('INSERT INTO persons (name, bio) VALUES (?, ?)', 
                            (name, bio))
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Ошибка при добавлении записи: {e}")
        return
    
    refresh_persons_list()
    messagebox.showinfo("Успешно", "Запись добавлена")
    get_listbox().focus_set()

def delete_person(event=None) -> None:
    listbox = gui_components['listbox']
    sel = listbox.curselection()
    
    if not sel:
        messagebox.showwarning("Ошибка", "Выберите запись для удаления")
        get_listbox().focus_set()
        return
    
    index = sel[0]
    person = app_state['persons'][index]
    
    if messagebox.askyesno("Подтверждение", f"Удалить '{person[1]}'?"):
        with sqlite3.connect('AmDB.db') as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM persons WHERE id = ?', (person[0],))
            
        refresh_persons_list()
        messagebox.showinfo("Успешно", "Запись удалена")

def edit_person(root: Tk, event=None) -> None:
    listbox = gui_components['listbox']
    sel = listbox.curselection()
    
    if not sel:
        messagebox.showwarning("Ошибка", "Выберите запись для изменения")
        get_listbox().focus_set()
        return
        
    index = sel[0]
    person = app_state['persons'][index]
    
    new_name = simpledialog.askstring("Изменить", "Введите новое имя:", 
                                    initialvalue=person[1], parent=root)
    if new_name is None:
        get_listbox().focus_set()
        return
    
    new_bio = simpledialog.askstring("Изменить", "Введите новую биографию:", 
                                    initialvalue=person[2], parent=root) or person[2]
    
    filepath = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
    new_photo = load_image(filepath) if filepath else None
    
    try:
        with sqlite3.connect('AmDB.db') as connection:
            cursor = connection.cursor()
            if new_photo:
                cursor.execute('''UPDATE persons SET name = ?, bio = ?, photo = ? 
                              WHERE id = ?''', (new_name, new_bio, new_photo, person[0]))
            else:
                cursor.execute('''UPDATE persons SET name = ?, bio = ? 
                              WHERE id = ?''', (new_name, new_bio, person[0]))
    except sqlite3.Error as e:
        messagebox.showerror("Ошибка БД", f"Ошибка при изменении записи: {e}")
        return
    
    refresh_persons_list()
    messagebox.showinfo("Успешно", "Запись изменена")
    get_listbox().focus_set()

def on_select(event=None) -> None:
    listbox = gui_components['listbox']
    sel = listbox.curselection()
    
    if not sel:
        return
        
    person = app_state['persons'][sel[0]]
    bio_text = gui_components['bio_text']
    photo_label = gui_components['photo_label']
    
    bio_text.delete(1.0, END)
    bio_text.insert(END, clean_bio_text(person[2]))

    if person[3]:
        try:
            photo_image = PhotoImage(data=person[3]).subsample(IMAGE_SUBSAMPLE)
            photo_label.image = photo_image
            photo_label.config(image=photo_image)
        except Exception as e:
            print(f"Ошибка загрузки изображения: {e}")
            photo_label.config(image=app_state['default_photo'])
    else:
        photo_label.config(image=app_state['default_photo'])

def open_menu(event=None) -> None:
    root = gui_components['listbox'].master
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    gui_components['fond_menu'].tk_popup(x, y)

def get_listbox() -> Listbox:
    return gui_components['listbox']

def create_statusbar(root: Tk) -> None:
    statusbar = Frame(root, bd=1, relief=SUNKEN)
    statusbar.pack(side=BOTTOM, fill=X)
    
    gui_components['user_label'] = Label(statusbar, 
                                      text=f"Пользователь: {app_state['current_username']}")
    gui_components['user_label'].pack(side=RIGHT, padx=10)
    
    info_label = Label(statusbar, 
                     text="F1-справка F2-добавить F3-удалить F4-изменить F10-меню")
    info_label.pack(side=LEFT, padx=10)

def create_main_menu(root: Tk) -> None:
    main_menu = Menu(root)
    fond_menu = Menu(main_menu, tearoff=0)
    
    fond_menu.add_command(label="Найти", command=find_person)
    fond_menu.add_command(label="Сменить пользователя", command=change_user)
    fond_menu.add_separator()
    fond_menu.add_command(label="Добавить", accelerator="F2", 
                        command=lambda: add_person(root))
    fond_menu.add_command(label="Удалить", accelerator="F3", command=delete_person)
    fond_menu.add_command(label="Изменить", accelerator="F4", 
                        command=lambda: edit_person(root))
    fond_menu.add_separator()
    fond_menu.add_command(label="Выход", accelerator="Ctrl+X", command=root.quit)
    
    help_menu = Menu(main_menu, tearoff=0)
    help_menu.add_command(label="Содержание", command=dialogs.show_help)
    help_menu.add_command(label="О программе", command=dialogs.show_about)
    
    main_menu.add_cascade(label="Фонд", menu=fond_menu)
    main_menu.add_cascade(label="Справка", menu=help_menu)
    
    gui_components['main_menu'] = main_menu
    gui_components['fond_menu'] = fond_menu
    root.config(menu=main_menu)

def create_gui(root: Tk, username: str) -> None:
    app_state['current_username'] = username
    init_default_photo()
    
    create_statusbar(root)
    create_main_menu(root)

    gui_components['listbox'] = Listbox(root, width=30)
    gui_components['listbox'].pack(side=LEFT, fill=Y, padx=[5, 0], pady=5)

    gui_components['photo_label'] = Label(root, width=600, bg="grey")
    gui_components['photo_label'].pack(side=LEFT, fill=Y, padx=5, pady=5)
    gui_components['photo_label'].default_image = app_state['default_photo']

    gui_components['bio_text'] = Text(root, wrap=WORD, width=50)
    gui_components['bio_text'].pack(side=LEFT, fill=BOTH, expand=True, padx=[0, 5], pady=5)

    gui_components['listbox'].bind("<<ListboxSelect>>", on_select)
    root.bind("<F10>", open_menu)
    
    refresh_persons_list()