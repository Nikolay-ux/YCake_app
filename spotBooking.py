from datetime import datetime

# Место с расписанием занятости
class Spot:
    def __init__(self, spot_id):
        self.spot_id = spot_id  # Уникальный идентификатор места
        self.schedule = {}  # Расписание занятости: {дата: [временные интервалы]}
    
    # Метод для бронирования временного интервала на указанную дату
    def book(self, date, time_slot):
        if date not in self.schedule:
            self.schedule[date] = []
        
        if time_slot in self.schedule[date]:
            return f"Место {self.spot_id} уже забронировано на {date} в {time_slot}."
        else:
            self.schedule[date].append(time_slot)
            return f"Место {self.spot_id} успешно забронировано на {date} в {time_slot}."
    
    # Проверка занятости места на указанную дату
    def is_booked(self, date, time_slot):
        if date in self.schedule and time_slot in self.schedule[date]:
            return True
        return False
    
    # Просмотр всех забронированных временных интервалов на определенную дату
    def get_bookings(self, date):
        if date in self.schedule:
            return self.schedule[date]
        return []


# Управление массивом мест
class PlaceManager:
    def __init__(self, num_spots):
        self.spots = [Spot(i) for i in range(1, num_spots + 1)]  # Создаем список мест
    
    # Бронирование конкретного места
    def book_spot(self, spot_id, date, time_slot):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.book(date, time_slot)
    
    # Проверка занятости конкретного места на определенное время
    def check_spot_availability(self, spot_id, date, time_slot):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.is_booked(date, time_slot)
    
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

# Бронирование
print(manager.book_spot(1, "2024-09-20", "10:00"))  # Место 1, 20 сентября, 10:00
print(manager.book_spot(2, "2024-09-20", "10:00"))  # Место 2, 20 сентября, 10:00
print(manager.book_spot(1, "2024-09-20", "10:00"))  # Попытка повторного бронирования места 1 на 20 сентября

# Проверка занятости
print(manager.check_spot_availability(1, "2024-09-20", "10:00"))  # Проверка занятости места 1 на 10:00
print(manager.check_spot_availability(3, "2024-09-20", "10:00"))  # Проверка занятости места 3 на 10:00

# Просмотр всех занятых мест на 20 сентября
print(manager.view_booked_spots("2024-09-20"))  # Какие места заняты на 20 сентября