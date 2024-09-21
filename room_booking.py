import sqlite3
from datetime import datetime, timedelta

class RoomBooking:
    def __init__(self, db_path):
        self.conn = sqlite3.connect(db_path)

    def is_room_available(self, room_id, date, start_time, duration):
        """Проверка доступности комнаты на заданное время"""
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + duration

        # Преобразуем время в удобный для сравнения формат
        start_time_str = start_datetime.strftime("%H:%M:%S")
        end_time_str = end_datetime.strftime("%H:%M:%S")

        with self.conn:
            # Запрос всех бронирований для указанной комнаты на указанную дату
            bookings = self.conn.execute('''SELECT time 
                                            FROM time 
                                            WHERE room_id = ? AND date = ?;''', 
                                         (room_id, date)).fetchall()

            # Проверяем, пересекаются ли уже существующие бронирования с желаемым временем
            for booking in bookings:
                existing_start_time = datetime.strptime(booking[0], "%H:%M:%S")
                existing_end_time = existing_start_time + timedelta(hours=1)  # Предполагаем 1 час на одно бронирование
                
                if start_datetime < existing_end_time and end_datetime > existing_start_time:
                    return False  # Комната занята

        return True  # Комната свободна

    def book_room(self, room_id, date, start_time, duration):
        """Бронирование комнаты"""
        if not self.is_room_available(room_id, date, start_time, duration):
            return f"Комната {room_id} уже забронирована на это время."

        # Вносим бронирование в базу данных
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        with self.conn:
            self.conn.execute('''INSERT INTO time (room_id, date, time) 
                                 VALUES (?, ?, ?);''',
                             (room_id, date, start_datetime.strftime("%H:%M:%S")))
        return f"Комната {room_id} успешно забронирована на {date} в {start_time} на {duration}."

    def get_booked_rooms(self, date):
        """Получение списка забронированных комнат на определённую дату"""
        with self.conn:
            bookings = self.conn.execute('''SELECT r.room_name, t.time
                                            FROM rooms r
                                            JOIN time t ON r.id = t.room_id
                                            WHERE t.date = ?;''', 
                                         (date,)).fetchall()
            return bookings if bookings else "Нет забронированных комнат на эту дату."

    def close(self):
        """Закрытие соединения с базой данных"""
        self.conn.close()
