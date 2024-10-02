from quart import Quart, render_template, jsonify, websocket, request
from quart_cors import cors
import asyncio
import websockets
import requests
import json
import logging
from config import CONFIG
import time
from CalcPoint import calcX, calcY, calculate_distance

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Quart(__name__)
app = cors(app, allow_origin="*")

# Инициализация начальных точек
initial_points = [
    {'sourceId': 'source1', 'x': 0, 'y': 0, 'id': 'initial1', 'receivedAt': int(time.time() * 1000)},
    {'sourceId': 'source2', 'x': 0, 'y': 100, 'id': 'initial2', 'receivedAt': int(time.time() * 1000)},
    {'sourceId': 'source3', 'x': 100, 'y': 0, 'id': 'initial3', 'receivedAt': int(time.time() * 1000)}
]

cached_data = []
clients = set()


def process_data(raw_data):
    #Обновляем только receivedAt для соответствующего sourceId
    for point in cached_data:
        if point['id'] == raw_data.get('id'):
            point['x'] = raw_data.get('x')
            point['y'] = raw_data.get('y')
            return point

    # Если sourceId не найден, создаем новую точку
    return {
        'id': raw_data.get('id'),
        'x': raw_data.get('x', 0),
        'y': raw_data.get('y', 0),
        'sentAt': raw_data.get('sentAt'),
        'receivedAt': raw_data.get('receivedAt')
    }


async def connect_to_source():
    while True:
        try:
            async with websockets.connect(CONFIG['SOURCE_WEBSOCKET_URI']) as websocket:
                logger.info("Подключено к WebSocket серверу источника данных")
                async for message in websocket:
                    await handle_message(message)
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"Соединение с источником данных закрыто: {e.reason}")
        except Exception as e:
            logger.error(f"Ошибка WebSocket при подключении к источнику: {e}")

        logger.info("Попытка переподключения к источнику через 5 секунд...")
        await asyncio.sleep(5)


async def handle_message(message):
    try:
        distance_data = []

        raw_data = json.loads(message)
        processed_data = process_data(raw_data)
        if processed_data not in cached_data:
            cached_data.append(processed_data)
        if len(cached_data) > 3:
            cached_data.pop(0)

        if len(cached_data) == 3:
            for point in cached_data:
                distance = calculate_distance(point['sentAt'], point['receivedAt'])
                distance_data.append((point['id'], distance))

        #print(distance_data)


        #print(cached_data)
        point_X = calcX(distance_data[0][1], distance_data[1][1], distance_data[2][1],
                        cached_data[0]['x'], cached_data[1]['x'], cached_data[2]['x'],
                        cached_data[0]['y'], cached_data[1]['y'], cached_data[2]['y'])

        point_Y = calcY(distance_data[0][1], distance_data[1][1], distance_data[2][1],
                        cached_data[0]['x'], cached_data[1]['x'], cached_data[2]['x'],
                        cached_data[0]['y'], cached_data[1]['y'], cached_data[2]['y'])

        # print(f"X: {point_X}")
        # print(f"Y: {point_Y}")

        point_OBJ = {
                'Object_Name': 'Object',
                'x_OBJ': point_X,
                'y_OBJ': point_Y,
        }
        processed_data.update(point_OBJ)

        #print(processed_data)
        #logger.info(f"Обработано сообщение: {processed_data}")
        await notify_clients(processed_data)
    except json.JSONDecodeError:
        logger.error(f"Получено некорректное JSON сообщение: {message}")
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")


async def notify_clients(data):
    if clients:
        disconnected_clients = set()
        for ws in clients:
            try:
                await ws.send(json.dumps(data))
            except Exception as e:
                logger.error(f"Ошибка при отправке данных клиенту: {e}")
                disconnected_clients.add(ws)

        clients.difference_update(disconnected_clients)


@app.before_serving
async def before_serving():
    app.add_background_task(connect_to_source)


@app.route('/')
async def index():
    url = "http://localhost:4001/config"
    response = requests.get(url, headers={})

    if response.status_code == 200:
        json_data = response.json()
    else:
        json_data = {"objectSpeed": 0}  # Значения по умолчанию на случай ошибки

    # Передаем json_data в шаблон index.html
    return await render_template('index.html', json_data=json_data)


@app.websocket('/ws')
async def ws():
    client = websocket._get_current_object()
    clients.add(client)
    try:
        for data in cached_data:
            await client.send(json.dumps(data))

        while True:
            data = await client.receive()
            logger.info(f"Получено сообщение от клиента: {data}")
            await client.send(json.dumps({"status": "received", "message": "Сообщение получено!"}))
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"Ошибка в WebSocket соединении с клиентом: {e}")
    finally:
        clients.remove(client)


@app.route('/get-data', methods=['GET'])
async def get_data():
    return jsonify(cached_data)

@app.route('/get-config', methods=['POST'])
async def get_config():
    url = "http://localhost:4001/config"

    response = requests.get(url, headers={"Content-Type": "application/json"})

    if response.status_code == 200:
        response_data = response.json()
        satelliteSpeed = response_data.get('satelliteSpeed', 0)
        objectSpeed = response_data.get('objectSpeed', 0)

        return jsonify({
            "objectSpeed": objectSpeed,
        })
    else:
        return jsonify({
            "status_code": response.status_code,
            "error": "Не удалось получить данные"
        })


@app.route('/send-config', methods=['POST', 'OPTIONS'])
async def send_config():
    if request.method == 'OPTIONS':
        # Preflight request. Reply successfully:
        response = await app.make_default_options_response()
        response.headers['Access-Control-Allow-Methods'] = 'POST'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    data = await request.get_json()

    url = "http://localhost:4001/config"

    try:
        response = requests.post(url,
                                 headers={"Content-Type": "application/json"},
                                 json=data)

        return jsonify({
            "status_code": response.status_code,
            "response": "Конфигурация обновлена" if response.status_code == 200 else "Ошибка обновления конфигурации",
            "updated_config": data
        })
    except requests.exceptions.RequestException as e:
        return jsonify({
            "status_code": 500,
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(host=CONFIG['HOST'], port=CONFIG['PORT'], debug=CONFIG['DEBUG'])