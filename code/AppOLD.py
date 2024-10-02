#App.py
from flask import Flask, render_template, jsonify, request
import plotly.graph_objects as go
import requests
from flask_cors import CORS
import websockets
import logging
import asyncio
import json
import time

from Client import get_data, connect
from CalcPoint import calcX, calcY, calculate_distance



app = Flask(__name__)
CORS(app)  # Разрешаем CORS для всех доменов и методов

previous_id = None
points = []  # Список для хранения точек

log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

async def start_websocket_connection():
    if not getattr(start_websocket_connection, "started", False):
        await connect()
        start_websocket_connection.started = True

# Запускаем цикл событий при запуске приложения
def start_event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(start_websocket_connection())
    loop.run_forever()

@app.route('/get-config', methods=['POST'])
def get_config():
    url = "http://localhost:4001/config"

    response = requests.get(url, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        response_data = response.json()
        satelliteSpeed = response_data.get('satelliteSpeed', 0)
        objectSpeed = response_data.get('objectSpeed', 0)

        return jsonify({
            "satelliteSpeed": satelliteSpeed,
            "objectSpeed": objectSpeed,
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Не удалось получить данные"
        })
@app.route('/')
def index():
    response = requests.post('http://localhost:5000/get-config')

    if response.status_code == 200:
        json_data = response.json()  # Преобразуем ответ в JSON
    else:
        json_data = {"error": "Не удалось получить конфигурацию"}

    return render_template('index.html', json_data=json_data)
    #return render_template("index.html")


@app.route('/graph-data')
def graph_data():
    global previous_id, points  # Указываем, что используем глобальные переменные
    try:
        data = asyncio.run(get_data())
        if data:
            x = data.get('x', 0)
            y = data.get('y', 0)
            sentAt = data.get('sentAt', 0)
            receivedAt = data.get('receivedAt', 0)
            id_satellite = data.get('id', 0)
            last_updated = time.time()

            if points:
                valid_points = [point for point in points if point['id_satellite'] != 'Object']  # Фильтруем только валидные точки

                if len(valid_points) <= 2:
                    existing_point = next((point for point in points if point['id_satellite'] == 'Object'),None)
                    if existing_point:
                      existing_point['marker'] = {'color': 'red', 'size': 12}

                if len(valid_points) >= 3:
                    distance_data = []
                    for point in valid_points:
                        distance = calculate_distance(point['sentAt'], point['receivedAt'])
                        distance_data.append((point['id_satellite'], distance))

                    #print(f"distance: {len(distance_data)}")
                    #print(f"valid_points: {len(valid_points)}")
                    # Печатаем данные для отладки
                    for i in range(len(distance_data)):
                        satellite_id = distance_data[i][0][-4:]  # Берем последние 4 символа ID
                        #print(f"{satellite_id}: {distance_data[i][1]}")

                        # Проверяем, существует ли точка в valid_points перед печатью
                        # if i < len(valid_points):  # Используем valid_points
                        #     print(f"{valid_points[i]['id_satellite'][-4:]}: {valid_points[i]['x']}, {valid_points[i]['y']}, {valid_points[i]['sentAt']}, {valid_points[i]['receivedAt']}")
                    if len(distance_data) & len(valid_points) >= 3:
                        point_X, point_Y = None, None
                        # print("Отладка входных данных для calcX и calcY:")
                        # print(f"distances: {[distance_data[0][1], distance_data[1][1], distance_data[2][1]]}")
                        # print(f"coordinates X: {[valid_points[0]['id_satellite'][-4:],valid_points[1]['id_satellite'][-4:],valid_points[2]['id_satellite'][-4:], valid_points[0]['x'], valid_points[1]['x'], valid_points[2]['x']]}")
                        # print(f"coordinates Y: {[valid_points[0]['id_satellite'][-4:],valid_points[1]['id_satellite'][-4:],valid_points[2]['id_satellite'][-4:], valid_points[0]['y'], valid_points[1]['y'], valid_points[2]['y']]}")

                        point_X = calcX(distance_data[0][1], distance_data[1][1], distance_data[2][1],
                                        valid_points[0]['x'], valid_points[1]['x'], valid_points[2]['x'],
                                        valid_points[0]['y'], valid_points[1]['y'], valid_points[2]['y'])

                        point_Y = calcY(distance_data[0][1], distance_data[1][1], distance_data[2][1],
                                        valid_points[0]['x'], valid_points[1]['x'], valid_points[2]['x'],
                                        valid_points[0]['y'], valid_points[1]['y'], valid_points[2]['y'])

                        # print(f"X: {point_X}")
                        # print(f"Y: {point_Y}")

                    Object_point = next((point for point in points if point['text'][0].startswith('Object')),None)

                    if Object_point:
                        if len(valid_points) == 4:
                            Object_point['x'] = point_X
                            Object_point['y'] = point_Y
                            Object_point['sentAt'] = 0
                            Object_point['receivedAt'] = 0
                            Object_point['last_updated'] = last_updated
                            Object_point['marker'] = {'color': 'orange', 'size': 12}
                        else:
                            # Если точка существует, обновляем её координаты
                            Object_point['x'] = point_X
                            Object_point['y'] = point_Y
                            Object_point['sentAt'] = 0
                            Object_point['receivedAt'] = 0
                            Object_point['last_updated'] = last_updated
                            Object_point['marker'] = {'color': 'green', 'size': 12}
                    else:
                        #satellite_id = distance_data[-1][0][-4:]
                        print(f"Объект {id_satellite[-4:]} появился в зоне")
                        points.append({
                            'x': point_X,
                            'y': point_Y,
                            'sentAt': 0,
                            'receivedAt': 0,
                            'id_satellite': 'Object',
                            'last_updated': last_updated,
                            'mode': 'markers+text',
                            'marker': {'color': 'green', 'size': 12},
                            'text': [f'Object'],
                            'textposition': 'top right'
                        })
                        #previous_id = id_satellite  # Обновляем предыдущее значение


            # Проверяем, существует ли уже точка с таким id_satellite
            existing_point = next((point for point in points if point['text'][0].startswith(id_satellite[-4:])), None)

            if existing_point:
                # Если точка существует, обновляем её координаты
                existing_point['x'] = x
                existing_point['y'] = y
                existing_point['sentAt'] = sentAt
                existing_point['receivedAt'] = receivedAt
                existing_point['last_updated'] = last_updated
            else:
                print(f"Спутник {id_satellite[-4:]} зашел в зону")
                # Если точки нет, добавляем новую
                points.append({
                    'x': x,
                    'y': y,
                    'sentAt': sentAt,
                    'receivedAt': receivedAt,
                    'id_satellite': id_satellite,
                    'last_updated': last_updated,
                    'mode': 'markers+text',
                    'marker': {'color': 'blue', 'size': 10},
                    'text': [f'{id_satellite[-4:]}'],
                    'textposition': 'top right'
                })
                previous_id = id_satellite  # Обновляем предыдущее значение

        # Удаляем устаревшие точки, кроме объекта
        current_time = time.time()
        points_to_remove = [point for point in points if current_time - point['last_updated'] > 7 and point['id_satellite'] != 'Object']

        # Печатаем информацию о выходе из зоны
        for point in points_to_remove:
            print(f"Спутник {(point['id_satellite'])[-4:]} вышел с зоны")

        # Обновляем список точек, исключая устаревшие
        points = [point for point in points if current_time - point['last_updated'] <= 7 or point['id_satellite'] == 'Object']

        if points:
            x_values = [point['x'] for point in points]
            y_values = [point['y'] for point in points]
            layout = {
                'xaxis': {
                    'title': 'X',
                    'range': [0, 120],  # Добавляем небольшой отступ
                },
                'yaxis': {
                    'title': 'Y',
                    'range': [0, 120],  # Добавляем небольшой отступ
                },
            }
        else:
            # Если points пустой, устанавливаем layout по умолчанию
            layout = {
                'xaxis': {
                    'title': 'X',
                    'range': [-210, 210],
                },
                'yaxis': {
                    'title': 'Y',
                    'range': [-210, 210],
                },
            }
        return jsonify({'data': [
            {'x': point['x'], 'y': point['y'], 'text': point['text'], 'marker': point['marker'], 'mode': point['mode'],
             'textposition': point['textposition']} for point in points], 'layout': layout})  # Возвращаем JSON
    except Exception as e:
        print("Ошибка:", e)
        return jsonify({"error": str(e)}), 500  # Возвращаем ошибку в формате JSON

@app.route('/send-config', methods=['POST'])
def send_config():
    # Получаем данные из запроса
    data = request.json

    # URL целевого сервера
    url = "http://localhost:4001/config"

    # Отправка PUT-запроса на целевой сервер
    response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    if response.status_code == 200:
        return jsonify({
            "status_code": response.status_code,
            "response": "Конфигурация обновлена",
            "updated_config": data  # Отправляем обновлённую конфигурацию
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Ошибка отправки конфигурации"
        })

if __name__ == "__main__":
    import threading
    event_loop_thread = threading.Thread(target=start_event_loop)
    event_loop_thread.start()

    app.run(debug=True)
