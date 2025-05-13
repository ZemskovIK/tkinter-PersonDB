from tkinter import *
from tkinter import messagebox, simpledialog, filedialog
import base64, dialogs, settings, database, sqlite3

user_label = None
current_username = None
photo_label = None
bio_text = None
listbox = None
photo_cache = None
persons = []

def get_current_username():
    global current_username
    return current_username

def change_user():
    global current_username, user_label
    new_name = settings.get_username(current_username)
    if new_name:
        current_username = new_name
        user_label.config(text=f"Пользователь: {new_name}")
        settings.save_settings(new_name)
        messagebox.showinfo("Успешно", f"Имя пользователя изменено на {new_name}")

def refresh_persons_list():
    global persons, listbox
    persons = database.get_all_persons()
    listbox.delete(0, END)
    for p in persons:
        listbox.insert(END, p[1])

def find_person():
    query = simpledialog.askstring("Поиск", "Введите имя для поиска:")
    if query:
        for i, person in enumerate(persons):
            if query.lower() in person[1].lower():
                listbox.selection_clear(0, END)
                listbox.selection_set(i)
                listbox.see(i)
                listbox.event_generate("<<ListboxSelect>>")
                break
        else:
            messagebox.showinfo("Поиск", "Ничего не найдено")

def add_person(root, event=None):
    name = simpledialog.askstring("Добавить", "Введите имя:", parent=root)
    if not name:
        return 
    bio = simpledialog.askstring("Добавить", "Введите биографию:", parent=root)
    bio = bio if bio else ""
    filepath = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
    img = None
    if filepath:
        try:
            with open(filepath, 'rb') as file:
                img = file.read()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить фото: {e}")
            return
    with sqlite3.connect('AmDB.db') as connection:
        cursor = connection.cursor()
        if img:
            cursor.execute('INSERT INTO persons (name, bio, photo) VALUES (?, ?, ?)', 
                          (name, bio, img))
        else:
            cursor.execute('INSERT INTO persons (name, bio) VALUES (?, ?)', 
                          (name, bio))
    
    refresh_persons_list()
    messagebox.showinfo("Успешно", "Запись добавлена")
    get_listbox().focus_set()

def delete_person(event=None):
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Ошибка", "Выберите запись для удаления")
        return
    index = sel[0]
    person = persons[index]
    if messagebox.askyesno("Подтверждение", f"Удалить '{person[1]}'?"):
        with sqlite3.connect('AmDB.db') as connection:
            cursor = connection.cursor()
            cursor.execute('DELETE FROM persons WHERE id = ?', (person[0],))
        refresh_persons_list()
        messagebox.showinfo("Успешно", "Запись удалена")

def edit_person(root, event=None):
    sel = listbox.curselection()
    if not sel:
        messagebox.showwarning("Ошибка", "Выберите запись для изменения")
        return
    index = sel[0]
    person = persons[index]
    
    new_name = simpledialog.askstring("Изменить", "Введите новое имя:", initialvalue=person[1], parent=root)
    if new_name is None:
        return
    
    new_bio = simpledialog.askstring("Изменить", "Введите новую биографию:", initialvalue=person[2], parent=root)
    new_bio = new_bio if new_bio is not None else person[2]
    filepath = filedialog.askopenfilename(filetypes=[("PNG Image", "*.png")])
    new_photo = None
    if filepath:
        with open(filepath, 'rb') as file:
            new_photo = file.read()
    
    with sqlite3.connect('AmDB.db') as connection:
        cursor = connection.cursor()
        if new_photo:
            cursor.execute('UPDATE persons SET name = ?, bio = ?, photo = ? WHERE id = ?', 
                          (new_name, new_bio, new_photo, person[0]))
        else:
            cursor.execute('UPDATE persons SET name = ?, bio = ? WHERE id = ?', 
                          (new_name, new_bio, person[0]))
    refresh_persons_list()
    messagebox.showinfo("Успешно", "Запись изменена")
    get_listbox().focus_set()

def create_gui(root, username):
    global photo_label, bio_text, listbox, photo_cache
    global user_label, current_username, persons, default_photo
    
    current_username = username
    default_photo = PhotoImage(file="./images/noimage.png")
    default_photo = default_photo.subsample(2)
    
    statusbar = Frame(root, bd=1, relief=SUNKEN)
    statusbar.pack(side=BOTTOM, fill=X)
    
    user_label = Label(statusbar, text=f"Пользователь: {username}")
    user_label.pack(side=RIGHT, padx=10)
    
    info_label = Label(statusbar, 
                       text= "F1-справка F2-добавить F3-удалить F4-изменить F10-меню")
    info_label.pack(side=LEFT, padx=10)
    
    photo_cache = {}
    photo_cache = {'default': default_photo}

    main_menu = Menu(root)
    fond_menu = Menu(main_menu, tearoff=0)
    fond_menu.add_command(label="Найти", command=find_person)
    fond_menu.add_command(label="Сменить пользователя",
                          command=change_user)
    fond_menu.add_separator()
    fond_menu.add_command(label="Добавить", accelerator="F2", command=lambda: add_person(root))
    fond_menu.add_command(label="Удалить", accelerator="F3", command=delete_person)
    fond_menu.add_command(label="Изменить", accelerator="F4", command=lambda: edit_person(root))
    fond_menu.add_separator()
    fond_menu.add_command(label="Выход", accelerator="Ctrl+X", command=root.quit)
    main_menu.add_cascade(label="Фонд", menu=fond_menu)

    help_menu = Menu(main_menu, tearoff=0)
    help_menu.add_command(label="Содержание", command=dialogs.show_help)
    help_menu.add_command(label="О программе", command=dialogs.show_about)
    main_menu.add_cascade(label="Справка", menu=help_menu)

    root.config(menu=main_menu)

    listbox = Listbox(root, width=30)
    listbox.pack(side=LEFT, fill=Y, padx=[5, 0], pady=5)

    photo_label = Label(root, width=600, bg="grey")
    photo_label.pack(side=LEFT, fill=Y, padx=5, pady=5)

    bio_text = Text(root, wrap=WORD, width=50)
    bio_text.pack(side=LEFT, fill=BOTH, expand=True, padx=[0, 5], pady=5)

    refresh_persons_list()
    
    def clean_bio(text):
        return ' '.join(line.strip() for line in text.split('\n'))
    
    def open_menu(event=None):
        x = root.winfo_rootx()
        y = root.winfo_rooty()
        fond_menu.tk_popup(x, y)

    def on_select(event=None):
        sel = listbox.curselection()
        if not sel:
            return
        index = sel[0]
        person = persons[index]
        pid, name, bio, blob = person

        bio_text.delete(1.0, END)
        bio_text.insert(END, clean_bio(bio))

        if blob:
            encoded = base64.b64encode(blob)
            img = PhotoImage(data=encoded)
            photo_cache[pid] = img.subsample(2)
            photo_label.config(image=photo_cache[pid], text="")
        else:
            photo_label.config(image=photo_cache['default'])

    listbox.bind("<<ListboxSelect>>", on_select)
    root.bind("<F10>", open_menu)
    
def get_listbox():
    return listbox