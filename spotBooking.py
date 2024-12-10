from datetime import datetime, timedelta

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

    # Проверка занятости места на указанную дату и время
    def is_booked(self, date, start_time, duration):
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + duration
        
        if date in self.schedule:
            for booking in self.schedule[date]:
                existing_start, existing_end = booking
                if start_datetime < existing_end and end_datetime > existing_start:
                    return True
        return False
    
    # Просмотр всех забронированных временных интервалов на определенную дату
    def get_bookings(self, date):
        if date in self.schedule:
            return [(booking[0].strftime("%H:%M"), booking[1].strftime("%H:%M")) for booking in self.schedule[date]]
        return []


# Управление массивом мест
class PlaceManager:
    def __init__(self, num_spots):
        self.spots = [Spot(i) for i in range(1, num_spots + 1)]  # Создаем список мест
    
    # Бронирование конкретного места
    def book_spot(self, spot_id, date, start_time, duration):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.book(date, start_time, duration)
    
    # Проверка занятости конкретного места на определенное время
    def check_spot_availability(self, spot_id, date, start_time, duration):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.is_booked(date, start_time, duration)
    
    # Просмотр всех занятых мест на определённую дату
    def view_booked_spots(self, date):
        booked_spots = {}
        for spot in self.spots:
            bookings = spot.get_bookings(date)
            if bookings:
                booked_spots[spot.spot_id] = bookings
        return booked_spots


# Пример использования
manager = PlaceManager(5)  # 5 мест

# Бронирование места 1 на 2 часа
print(manager.book_spot(1, "2024-09-20", "10:00", timedelta(hours=2)))

# Попытка бронирования на 15 минут (ошибка)
print(manager.book_spot(2, "2024-09-20", "10:00", timedelta(minutes=15)))

# Попытка бронирования места 1 на тот же временной интервал (ошибка)
print(manager.book_spot(1, "2024-09-20", "10:30", timedelta(hours=1)))

# Проверка занятости
print(manager.check_spot_availability(1, "2024-09-20", "10:00", timedelta(hours=2)))  # Место занято
print(manager.check_spot_availability(3, "2024-09-20", "10:00", timedelta(hours=1)))  # Место свободно

# Просмотр всех занятых мест на 20 сентября
print(manager.view_booked_spots("2024-09-20"))  # Какие места заняты на 20 сентября