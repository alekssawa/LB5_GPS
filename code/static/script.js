document.addEventListener('DOMContentLoaded', function() {
    let socket;
    let pointData = {};
    let traceIndex = 0;
    let pointTimers = {};

    //const reconnectButton = document.getElementById('reconnect');
    const responseMessage = document.getElementById('responseMessage');

    const layout = {
        xaxis: { title: 'X', range: [0, 120] },
        yaxis: { title: 'Y', range: [0, 120] },
        width: 600,
        height: 600
    };

    // Инициализация графика
    if(typeof Plotly !== 'undefined') {
        console.log("Plotly is loaded");
        Plotly.newPlot('graph', [], layout);
    } else {
        console.error("Plotly is not loaded");
    }

    function connect() {
        console.log("Attempting to connect...");
        socket = new WebSocket('ws://' + window.location.host + '/ws');

        socket.onopen = function(event) {
            console.log("Соединение установлено");
        };

        socket.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateGraph(data);
        };
    }

    function updateGraph(data) {
        const hoverTextSource = `ID: ${data.id.slice(-4)}<br>X: ${data.x}<br>Y: ${data.y}<br>receivedAt: ${data.receivedAt}`;

        // Обновляем таймер для точки
        if (pointTimers[data.id]) {
            clearTimeout(pointTimers[data.id]);
        }
        pointTimers[data.id] = setTimeout(() => {
            removePoint(data.id);
        }, 2000);

        if (data.id in pointData) {
            // Обновление существующей точки
            const traceIndex = pointData[data.id].traceIndex;

            Plotly.restyle('graph', {
                x: [[data.x]],
                y: [[data.y]],
                text: [[hoverTextSource]]
            }, [traceIndex]).catch(error => {
                console.error('Error updating point:', error);
            });

            // Обновляем данные точки
            pointData[data.id].x = data.x;
            pointData[data.id].y = data.y;
            pointData[data.id].receivedAt = data.receivedAt;
        } else {
            // Добавление новой точки
            const newTrace = {
                name: data.id.slice(-4),
                x: [data.x],
                y: [data.y],
                text: [data.id],
                mode: 'markers',
                type: 'scatter',
                marker: { size: 10 }
            };

            Plotly.addTraces('graph', newTrace).then(() => {
                pointData[data.id] = {
                    traceIndex: traceIndex,
                    x: data.x,
                    y: data.y,
                    receivedAt: data.receivedAt
                };
                traceIndex++;
            }).catch(error => {
                console.error('Error adding new point:', error);
            });
        }
    }

    function removePoint(id) {
        if (id in pointData) {
            const removeIndex = pointData[id].traceIndex;

            Plotly.deleteTraces('graph', [removeIndex]).then(() => {
                // Обновляем индексы для оставшихся точек
                Object.keys(pointData).forEach(pointId => {
                    if (pointData[pointId].traceIndex > removeIndex) {
                        pointData[pointId].traceIndex--;
                    }
                });

                delete pointData[id];
                delete pointTimers[id];
                traceIndex--;
            }).catch(error => {
                console.error('Error removing point:', error);
            });
        }
    }

    function submitConfig() {
        const objectSpeed = document.getElementById('objectSpeedInput').value;
        const config = {
            objectSpeed: parseInt(objectSpeed, 10)
        };

        fetch('/send-config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.status_code === 200) {
                document.getElementById('objectSpeed').innerText = config.objectSpeed;
                responseMessage.innerText = 'Конфігурація успішно оновлена.';
                responseMessage.style.color = 'green';
            } else {
                throw new Error(data.error || 'Невідома помилка');
            }
        })
        .catch(error => {
            console.error('Помилка:', error);
            responseMessage.innerText = 'Помилка: ' + error.message;
            responseMessage.style.color = 'red';
        });
    }

    // Инициализация подключения
    connect();

    // Обработчик события выгрузки страницы
    window.addEventListener('beforeunload', () => {
        Object.keys(pointTimers).forEach(id => {
            clearTimeout(pointTimers[id]);
        });
    });

    // Делаем функцию submitConfig доступной глобально
    window.submitConfig = submitConfig;
});