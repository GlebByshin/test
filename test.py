from flask import Flask, render_template_string
API_KEY = "28436f7f-6d23-4241-a820-a0a243cb8ac6"

app = Flask(__name__)

INDEX_HTML = """
<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
<title>Туристический маршрут — Пермский край</title>
<style>
  body { font-family: Arial; margin: 0; padding: 0; }
  #map { width: 100%; height: 60vh; }
  .controls { padding: 15px; max-width: 800px; margin: auto; }
  .place-item { border: 1px solid #ddd; padding: 10px; border-radius: 6px; margin: 5px 0; cursor: move; background: white; }
  .place-item:hover { background: #f0f0f0; }
  .place-item.dragging { opacity: 0.5; background: #e0e0e0; }
  #desc { margin-top: 15px; padding: 10px; font-size: 14px; border: 1px solid #ccc; border-radius: 6px; }
  .drag-handle { cursor: move; margin-right: 8px; color: #666; }
  .checkbox-container { margin: 15px 0; display: flex; align-items: center; gap: 8px; }
  .location-status { margin-left: 10px; font-size: 14px; color: #666; }
  .location-success { color: green; }
  .location-error { color: red; }
  button { padding: 10px 15px; margin: 5px; cursor: pointer; }
  #detect-location { background: #4CAF50; color: white; border: none; border-radius: 4px; }
  #build_route { background: #2196F3; color: white; border: none; border-radius: 4px; }
</style>
<script src="https://api-maps.yandex.ru/2.1/?apikey={{api_key}}&lang=ru_RU"></script>
</head>

<body>
  <div id="map"></div>

  <div class="controls">
    <button id="detect-location">📍 Определить мое местоположение</button>
    <button id="build_route">🗺️ Построить маршрут</button>

    <div class="checkbox-container">
      <input type="checkbox" id="start-from-me">
      <label for="start-from-me">Начать маршрут от моей позиции</label>
      <span id="location-status" class="location-status"></span>
    </div>

    <h3>Точки маршрута (перетащите для изменения порядка):</h3>
    <div id="places_list"></div>

    <div id="desc"><i>Нажмите на место, чтобы увидеть описание</i></div>
  </div>

<script>
ymaps.ready(init);

function init() {
  // 📍 Заданные точки маршрута
  let PLACES = [
    { name: "Кунгурская ледяная пещера", coords: [57.4267, 56.9562], desc: "Одна из самых известных карстовых пещер России." },
    { name: "132fix2332 — смотровая площадка", coords: [58.2905, 57.8192], desc: "Живописный вид на реку Чусовую." },
    { name: "Пермь — Набережная Камы", coords: [58.0105, 56.2502], desc: "Центральная набережная города Перми." }
  ];

  let map = new ymaps.Map("map", { center: [57.8, 56.5], zoom: 7 });
  let currentRoute = null;
  let myLocation = null;
  let myLocationMarker = null;

  // Функция для обновления маркеров на карте
  function updateMapMarkers() {
    // Удаляем старые маркеры (кроме маркера моего местоположения)
    map.geoObjects.removeAll();
    
    // Добавляем маркер моего местоположения если он есть
    if (myLocationMarker) {
      map.geoObjects.add(myLocationMarker);
    }
    
    // Добавляем новые POI метки на карту
    PLACES.forEach((p, i) => {
      map.geoObjects.add(new ymaps.Placemark(p.coords, {
        balloonContent: `<b>${p.name}</b><br>${p.desc}`,
        iconCaption: `${i + 1}. ${p.name}`
      }, {
        preset: 'islands#blueIcon'
      }));
    });
  }

  // Функция для обновления списка мест
  function updatePlacesList() {
    const listContainer = document.getElementById("places_list");
    listContainer.innerHTML = '';
    
    PLACES.forEach((p, i) => {
      let div = document.createElement("div");
      div.className = "place-item";
      div.draggable = true;
      div.dataset.index = i;
      div.innerHTML = `<span class="drag-handle">☰</span> ${i + 1}. ${p.name}`;
      
      // Клик для показа описания
      div.onclick = (e) => {
        if (!e.target.classList.contains('drag-handle')) {
          document.getElementById("desc").innerHTML = `<b>${p.name}</b><br>${p.desc}`;
          map.setCenter(p.coords, 10);
        }
      };
      
      // Drag & Drop события
      div.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', i);
        div.classList.add('dragging');
      });
      
      div.addEventListener('dragend', () => {
        document.querySelectorAll('.place-item').forEach(item => {
          item.classList.remove('dragging');
        });
      });
      
      div.addEventListener('dragover', (e) => {
        e.preventDefault();
      });
      
      div.addEventListener('drop', (e) => {
        e.preventDefault();
        const fromIndex = parseInt(e.dataTransfer.getData('text/plain'));
        const toIndex = parseInt(div.dataset.index);
        
        if (fromIndex !== toIndex) {
          // Перемещаем элемент в массиве
          const [movedItem] = PLACES.splice(fromIndex, 1);
          PLACES.splice(toIndex, 0, movedItem);
          
          // Обновляем интерфейс
          updatePlacesList();
          updateMapMarkers();
          
          // Перестраиваем маршрут если он был построен
          if (currentRoute) {
            buildRoute();
          }
        }
      });
      
      listContainer.appendChild(div);
    });
  }

  // Функция определения местоположения
  function detectLocation() {
    const statusElement = document.getElementById('location-status');
    statusElement.textContent = 'Определяем...';
    statusElement.className = 'location-status';
    
    if (!navigator.geolocation) {
      statusElement.textContent = 'Геолокация не поддерживается браузером';
      statusElement.classList.add('location-error');
      return;
    }
    
    navigator.geolocation.getCurrentPosition(
      function(position) {
        myLocation = [position.coords.latitude, position.coords.longitude];
        
        // Создаем или обновляем маркер местоположения
        if (myLocationMarker) {
          map.geoObjects.remove(myLocationMarker);
        }
        
        myLocationMarker = new ymaps.Placemark(myLocation, {
          balloonContent: 'Ваше местоположение',
          iconCaption: 'Я здесь'
        }, {
          preset: 'islands#greenDotIconWithCaption'
        });
        
        map.geoObjects.add(myLocationMarker);
        map.setCenter(myLocation, 12);
        
        statusElement.textContent = 'Местоположение определено!';
        statusElement.classList.add('location-success');
        
        // Включаем галочку "начать от моей позиции"
        document.getElementById('start-from-me').disabled = false;
      },
      function(error) {
        let errorMessage = 'Не удалось определить местоположение';
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Доступ к геолокации запрещен';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Информация о местоположении недоступна';
            break;
          case error.TIMEOUT:
            errorMessage = 'Время ожидания истекло';
            break;
        }
        statusElement.textContent = errorMessage;
        statusElement.classList.add('location-error');
        document.getElementById('start-from-me').disabled = true;
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  }

  // Функция построения маршрута
  function buildRoute() {
    if (PLACES.length < 2) return;
    
    const startFromMe = document.getElementById('start-from-me').checked;
    
    if (startFromMe && !myLocation) {
      alert('Сначала определите ваше местоположение или снимите галочку "Начать маршрут от моей позиции"');
      return;
    }
    
    // Удаляем предыдущий маршрут
    if (currentRoute) {
      map.geoObjects.remove(currentRoute);
    }

    let points = PLACES.map(p => p.coords);
    
    // Если выбрано "начать от моей позиции", добавляем точку в начало
    if (startFromMe) {
      points = [myLocation, ...points];
    }
    
    ymaps.route(points, { routingMode: "auto" }).then(route => {
      currentRoute = route;
      map.geoObjects.add(route);
      map.setBounds(route.getBounds(), { checkZoomRange: true, zoomMargin: 30 });
    }, err => alert("Ошибка построения маршрута: " + err.message));
  }

  // Инициализация
  updateMapMarkers();
  updatePlacesList();

  // Назначаем обработчики событий
  document.getElementById("detect-location").addEventListener("click", detectLocation);
  document.getElementById("build_route").addEventListener("click", buildRoute);
  
  // Изначально отключаем галочку пока местоположение не определено
  document.getElementById('start-from-me').disabled = true;
  
  // Обработчик изменения галочки
  document.getElementById('start-from-me').addEventListener('change', function() {
    if (this.checked && !myLocation) {
      detectLocation();
    }
  });
}
</script>
</body>
</html>
"""

@app.route("/")
def index():
    response = app.make_response(render_template_string(INDEX_HTML, api_key=API_KEY))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

if __name__ == "__main__":
    app.run(debug=True)
