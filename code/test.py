def calculate_distance(send_time_ms, receive_time_ms):
    # Скорость света в метрах в секунду
    speed_of_light = 299792458

    # Вычисляем время в пути в секундах
    time_taken_seconds = (receive_time_ms - send_time_ms) / 1000

    # Расчет расстояния
    distance = speed_of_light * time_taken_seconds/ 1000
    return distance


# Пример использования
send_time = 1727210159257  # время отправки в миллисекундах
receive_time = 1727210159257.1162  # время получения в миллисекундах
distance = calculate_distance(send_time, receive_time)
print(f"Расстояние: {distance} км")