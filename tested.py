import sqlite3

# Подключение к базе данных (если база не существует, она будет создана)
conn = sqlite3.connect('1.db')

# Создание курсора для выполнения SQL-запросов
cur = conn.cursor()

# SQL-запрос для добавления данных
sql_query = '''INSERT INTO rooms (ID, room_name, room_position) VALUES (?, ?, ?)'''

# Данные для вставки
data = (3, 'dramma','queen')

# Выполняем запрос на добавление данных
cur.execute(sql_query, data)

# Фиксация изменений
conn.commit()

# Закрытие соединения
conn.close()

print("Данные успешно добавлены!")
