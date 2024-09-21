import sqlite3
from datetime import datetime
date = "2024-09-22"
spot_id = 2

        
conn = sqlite3.connect('1.db')
cursor = conn.cursor()

# Generate all possible time slots from 8:00 to 18:00
all_slots = [f'{hour:02}.{minute:02}' for hour in range(8, 18) for minute in [0, 30]]

print (date)
cursor.execute('SELECT time FROM time WHERE date = ? AND home_id = ? ORDER BY time', (date, spot_id,))

occupied_slots = [slot[0] for slot in cursor.fetchall()]
occupied_slots = [slot[:5] for slot in occupied_slots]

# Filter out the occupied slots
print(occupied_slots)
# Преобразование времени в формат 'hh:mm' в объекты datetime.time
occupied_slots_time = [datetime.strptime(slot, '%H:%M').time() for slot in occupied_slots]

# Фильтрация доступных слотов
available_slots = []
for slot in all_slots:
    slot_time = datetime.strptime(slot, '%H.%M').time()
    if slot_time not in occupied_slots_time:
        available_slots.append(slot)

# Вывод доступных слотов
print("available slots:")
print(available_slots)
# Close the connection
conn.close()