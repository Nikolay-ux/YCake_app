import sqlite3

# Подключение к базе данных
conn = sqlite3.connect('1.db')  # Замените на ваше название базы данных
cursor = conn.cursor()

# SQL-запрос
query = """
SELECT room_position, GROUP_CONCAT(room_name) AS rooms
FROM rooms
GROUP BY room_position;
"""

# Выполнение запроса
cursor.execute(query)
results = cursor.fetchall()

# Массив для хранения городов
cities = []

# Вывод результата и заполнение массива городов
for row in results:
    cities.append(row[0])  # Добавляем город в массив
    print(f"Город: {row[0]}, Комнаты: {row[1]}")

# Вывод массива городов
print("Список городов:", cities)

# Закрытие соединения
conn.close()
