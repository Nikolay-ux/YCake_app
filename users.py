import sqlite3

def db_connect():
    return sqlite3.connect('1.db')

def check_user_in_db(username, password):
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM tags WHERE tg_mail = ? AND password = ?', (username, password))
    result = cursor.fetchone()

    conn.close()
    
    return result is not None
