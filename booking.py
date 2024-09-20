from datetime import datetime, timedelta
import sqlite3
# Место с расписанием занятости
class Spot:
    def __init__(self, spot_id):
        self.spot_id = spot_id  # Уникальный идентификатор места
        self.schedule = {}  # Расписание занятости: {дата: [временные интервалы]}
    
    # Метод для бронирования временного интервала на указанную дату
    def book(self, date, start_time, duration):
        # Проверка на длительность бронирования (30 минут - 3 часа)
        if duration < timedelta(minutes=30) or duration > timedelta(hours=3):
            return f"Ошибка: Длительность бронирования должна быть от 30 минут до 3 часов."
        
        # Конвертируем строку даты в объект datetime
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + duration
        
        if date not in self.schedule:
            self.schedule[date] = []
        
        # Проверяем, не пересекается ли это время с существующими бронированиями
        for booking in self.schedule[date]:
            existing_start, existing_end = booking
            if start_datetime < existing_end and end_datetime > existing_start:
                return f"Место {self.spot_id} уже забронировано в это время."
        
        # Добавляем бронирование (в виде временного интервала)
        self.schedule[date].append((start_datetime, end_datetime))
        return f"Место {self.spot_id} успешно забронировано с {start_time} на {duration}."


# Управление массивом мест
class PlaceManager:
    def __init__(self):
        # Connect to the database
        conn = sqlite3.connect('1.db')
        cursor = conn.cursor()

        # Execute the query to get the number of rows
        cursor.execute('SELECT COUNT(*) FROM rooms')
        num_spots = cursor.fetchone()[0]

        # Close the connection
        conn.close()
        self.spots = [Spot(i) for i in range(1, num_spots + 1)]  # Создаем список мест
    def num_spots(self):
        return len(self.spots)
    
    # Бронирование конкретного места
    def book_spot(self, spot_id, date, start_time, duration):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.book(date, start_time, duration)
    
    # Проверка занятости конкретного места на определенное время
    def check_spot_availability(self, spot_id, date):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        conn = sqlite3.connect('1.db')
        cursor = conn.cursor()

        # Generate all possible time slots from 8:00 to 18:00
        all_slots = [f'{str(hour).zfill(2)}:00' for hour in range(8, 18)]

        # Query to get the occupied slots from the table
        print (date)
        cursor.execute('SELECT time FROM time WHERE date = ? ORDER BY time', (date,))
        occupied_slots = [slot[0] for slot in cursor.fetchall()]

        # Filter out the occupied slots
        available_slots = [slot for slot in all_slots if slot not in occupied_slots]

        # Print the available slots
        print(available_slots)

        # Close the connection
        conn.close()
       
    
    # Просмотр всех занятых мест на определённую дату
    def view_booked_spots(self, date):
        booked_spots = {}
        for spot in self.spots:
            bookings = spot.get_bookings(date)
            if bookings:
                booked_spots[spot.spot_id] = bookings
        return booked_spots
