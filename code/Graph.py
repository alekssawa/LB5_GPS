import plotly.express as px
import pandas as pd


def calculate_distance(send_time_ms, receive_time_ms):
    # Скорость света в метрах в секунду
    speed_of_light = 299792458

    # Вычисляем время в пути в секундах
    time_taken_seconds = (receive_time_ms - send_time_ms) / 1000

    # Расчет расстояния
    distance = speed_of_light * time_taken_seconds/ 1000
    return distance


# Данные для трех точек
data = {
    'x': [45.898196493182326, 57.90571329683722, 0.7636837237142386],
    'y': [16.62746438070607, 0.5670603664211247, 14.785290919844137],
    'sentAt' : [1727221075466, 1727221071825, 1727221074471],
    'receivedAt' : [1727221075466.2349, 1727221071825.2805, 1727221074471.315],
    'label': ['SL1', 'SL2', 'SL3']
}
distance_data = []
for i in range(len(data['x'])):
    distance = calculate_distance(data['sentAt'][i], data['receivedAt'][i])
    distance_data.append((data['label'][i], distance))

# Вывод результата
for label, distance in distance_data:
    print(f"{label}: {distance} км")

def AD(x1,x2):
    result=2*(x2-x1)
    return result

def BE(y1,y2):
    result=2*(y2-y1)
    return result

def CF(r1,r2,x1,x2,y1,y2):
    result=r1**2 - r2**2 - x1**2 + x2**2 - y1**2 + y2**2
    return result

# def D(x2,x3):
#     result=2*(x3-x2)
#     return result
#
# def E(y2,y3):
#     result=2*(y3-y2)
#     return result
#
# def F(r2,r3,x2,x3,y2,y3):
#     result = r2**2 - r3**2 - x2**2 + x3**2 - y2**2 + y3**2
#     return result


print(f"A: {AD(data['x'][0],data['x'][1])}")
print(f"B: {BE(data['y'][0],data['y'][1])}")
print(f"C: {CF(distance_data[0][1],distance_data[1][1], data['x'][0],data['x'][1],data['y'][0],data['y'][1])}")

print(f"D: {AD(data['x'][1],data['x'][2])}")
print(f"E: {BE(data['y'][1],data['y'][2])}")
print(f"F: {CF(distance_data[1][1],distance_data[2][1], data['x'][1],data['x'][2],data['y'][1],data['y'][2])}")

print()
def calcX(r1,r2,r3,x1,x2,x3,y1,y2,y3):
    result = ((CF(r1,r2,x1,x2,y1,y2) * BE(y2, y3) - CF(r2, r3, x2, x3, y2, y3) * BE(y1, y2))/
              (BE(y2, y3) * AD(x1, x2) - BE(y1, y2) * AD(x2, x3)))
    print(f"X: {result}")
    return result


def calcY(r1,r2,r3,x1,x2,x3,y1,y2,y3):
    result = ((CF(r1,r2,x1,x2,y1,y2) * AD(x2, x3) - AD(x1, x2) * CF(r2, r3, x2, x3, y2, y3))/
              (BE(y1, y2) * AD(x2, x3) - AD(x1, x2) * BE(y2, y3)))
    print(f"Y: {result}")
    return result

point_X = calcX(distance_data[0][1],distance_data[1][1],distance_data[2][1],
                data['x'][0],data['x'][1],data['x'][2],
                data['y'][0],data['y'][1], data['y'][2],)

point_Y = calcY(distance_data[0][1],distance_data[1][1],distance_data[2][1],
      data['x'][0],data['x'][1],data['x'][2],
      data['y'][0],data['y'][1], data['y'][2],)



# Создание DataFrame
df = pd.DataFrame(data)

new_point = {
    'x': [point_X],
    'y': [point_Y],
    'sentAt': [1727210151000],
    'receivedAt': [1727210151000.1234],
    'label': ['Point']
}
new_df = pd.DataFrame(new_point)
df = pd.concat([df, new_df], ignore_index=True)

# Построение графика
fig = px.scatter(df, x='x', y='y', text='label')
fig.update_traces(textposition='top center')

# Отображение графика
fig.show()