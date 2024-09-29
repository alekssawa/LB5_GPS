def calculate_distance(send_time_ms, receive_time_ms):
    # Скорость света в метрах в секунду
    speed_of_light = 299792458

    # Вычисляем время в пути в секундах
    time_taken_seconds = (receive_time_ms - send_time_ms) / 1000

    # Расчет расстояния
    distance = speed_of_light * time_taken_seconds/ 1000
    return distance


# Данные для трех точек
# data = {
#     'x': [40.61748712448968, 98.69851230360301, 13.545419945739612],
#     'y': [90.7294255338162, 41.28650822235042, 36.845276799677485],
#     'sentAt' : [1727210151749, 1727210157892, 1727210159257],
#     'receivedAt' : [1727210151749.1511, 1727210157892.1724, 1727210159257.1162],
#     'label': ['SL1', 'SL2', 'SL3']
# }
#distance_data = []
# for i in range(len(data['x'])):
#     distance = calculate_distance(data['sentAt'][i], data['receivedAt'][i])
#     distance_data.append((data['label'][i], distance))
#
# # Вывод результата
# for label, distance in distance_data:
#     print(f"{label}: {distance} км")

def AD(x1,x2):
    result=2*(x2-x1)
    return result

def BE(y1,y2):
    result=2*(y2-y1)
    return result

def CF(r1,r2,x1,x2,y1,y2):
    result=r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    return result

def calcX(r1,r2,r3,x1,x2,x3,y1,y2,y3):
    result = ((CF(r1,r2,x1,x2,y1,y2) * BE(y2, y3) - CF(r2, r3, x2, x3, y2, y3) * BE(y1, y2))/
              (BE(y2, y3) * AD(x1, x2) - BE(y1, y2) * AD(x2, x3)))
    #print(f"X: {result}")
    return result


def calcY(r1,r2,r3,x1,x2,x3,y1,y2,y3):
    result = ((CF(r1,r2,x1,x2,y1,y2) * AD(x2, x3) - AD(x1, x2) * CF(r2, r3, x2, x3, y2, y3))/
              (BE(y1, y2) * AD(x2, x3) - AD(x1, x2) * BE(y2, y3)))
    #print(f"Y: {result}")
    return result

# point_X = calcX(distance_data[0][1],distance_data[1][1],distance_data[2][1],
#                 data['x'][0],data['x'][1],data['x'][2],
#                 data['y'][0],data['y'][1], data['y'][2],)
#
# point_Y = calcY(distance_data[0][1],distance_data[1][1],distance_data[2][1],
#       data['x'][0],data['x'][1],data['x'][2],
#       data['y'][0],data['y'][1], data['y'][2],)
