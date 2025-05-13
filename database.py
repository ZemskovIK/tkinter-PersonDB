import sqlite3

def create_database():
    with sqlite3.connect('AmDB.db') as connection:
        cursor = connection.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Persons (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            bio TEXT,
            photo BLOB
        )
        ''')
        
def get_all_persons():
    connection = sqlite3.connect("AmDB.db")
    cursor = connection.cursor()
    cursor.execute("SELECT id, name, bio, photo FROM persons ORDER BY name")
    rows = cursor.fetchall()
    connection.close()
    return rows