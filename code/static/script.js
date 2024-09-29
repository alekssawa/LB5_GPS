function updateGraph(data) {
            // Создаем новый массив с данными
            const graphData = data.data.map(point => ({
                x: [point.x],  // массив x
                y: [point.y],  // массив y
                mode: point.mode,
                marker: point.marker,
                text: point.text,
                textposition: point.textposition
            }));

            Plotly.react('graph', graphData, data.layout);
        }

function fetchData() {
    fetch('/graph-data')
        .then(response => response.json())
        .then(data => {
            // console.log(data);  // Отладочное сообщение
            updateGraph(data);  // Обновляем график
        })
        .catch(error => console.error('Ошибка:', error));
}

// Запускаем функцию обновления данных
setInterval(fetchData, 300);  // Обновляем график каждые 1 секунду

// Функция для отправки новой конфигурации
function submitConfig() {
    const satelliteSpeed = document.getElementById('satelliteSpeedInput').value;
    const objectSpeed = document.getElementById('objectSpeedInput').value;

    const config = {
        satelliteSpeed: parseInt(satelliteSpeed, 10),
        objectSpeed: parseInt(objectSpeed, 10),
    };

    fetch('http://127.0.0.1:5000/send-config', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(config)
    })
    .then(response => response.json())
    .then(data => {
        if (data.status_code === 200) {
            // Обновляем данные на странице
            document.getElementById('satelliteSpeed').innerText = config.satelliteSpeed;
            document.getElementById('objectSpeed').innerText = config.objectSpeed;

            // Выводим сообщение об успешном обновлении
            document.getElementById('responseMessage').innerText = 'Конфігурація успішно оновлена.';
        } else {
            // Выводим сообщение об ошибке
            document.getElementById('responseMessage').innerText = 'Ошибка: ' + data.error;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        document.getElementById('responseMessage').innerText = 'Ошибка: ' + error;
    });
}