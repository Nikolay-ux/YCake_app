from spot import Spot

class PlaceManager:
    def __init__(self, num_spots):
        self.spots = [Spot(i) for i in range(1, num_spots + 1)]  # Создаем список мест
    
    def book_spot(self, spot_id, date, start_time, duration):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.book(date, start_time, duration)
    
    def check_spot_availability(self, spot_id, date, start_time, duration):
        if spot_id < 1 or spot_id > len(self.spots):
            return "Ошибка: Неверный номер места."
        
        spot = self.spots[spot_id - 1]
        return spot.is_booked(date, start_time, duration)
    
    def view_booked_spots(self, date):
        booked_spots = {}
        for spot in self.spots:
            bookings = spot.get_bookings(date)
            if bookings:
                booked_spots[spot.spot_id] = bookings
        return booked_spots
