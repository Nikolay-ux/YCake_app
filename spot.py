from datetime import datetime, timedelta

class Spot:
    def __init__(self, spot_id):
        self.spot_id = spot_id  # Уникальный идентификатор места
        self.schedule = {}  # Расписание занятости: {дата: [временные интервалы]}
    
    def book(self, date, start_time, duration):
        if duration < timedelta(minutes=30) or duration > timedelta(hours=3):
            return f"Ошибка: Длительность бронирования должна быть от 30 минут до 3 часов."
        
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + duration
        
        if date not in self.schedule:
            self.schedule[date] = []
        
        for booking in self.schedule[date]:
            existing_start, existing_end = booking
            if start_datetime < existing_end and end_datetime > existing_start:
                return f"Место {self.spot_id} уже забронировано в это время."
        
        self.schedule[date].append((start_datetime, end_datetime))
        return f"Место {self.spot_id} успешно забронировано с {start_time} на {duration}."

    def is_booked(self, date, start_time, duration):
        start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end_datetime = start_datetime + duration
        
        if date in self.schedule:
            for booking in self.schedule[date]:
                existing_start, existing_end = booking
                if start_datetime < existing_end and end_datetime > existing_start:
                    return True
        return False

    def get_bookings(self, date):
        if date in self.schedule:
            return [(booking[0].strftime("%H:%M"), booking[1].strftime("%H:%M")) for booking in self.schedule[date]]
        return []
