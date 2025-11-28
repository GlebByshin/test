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
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #2c3e50; }
  #map { width: 100%; height: 65vh; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
  .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
  .header h1 { font-size: 28px; font-weight: 600; margin-bottom: 5px; }
  .header p { font-size: 14px; opacity: 0.9; }
  .controls { padding: 25px; max-width: 900px; margin: 0 auto; background: white; margin-top: -40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.08); position: relative; z-index: 10; }
  .controls h3 { margin-top: 20px; margin-bottom: 12px; color: #2c3e50; font-size: 16px; font-weight: 600; }
  .button-group { display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap; }
  button { padding: 12px 20px; cursor: pointer; border: none; border-radius: 6px; font-size: 14px; font-weight: 500; transition: all 0.3s ease; }
  #detect-location { background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%); color: white; }
  #detect-location:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(76, 175, 80, 0.3); }
  #build_route { background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; }
  #build_route:hover { transform: translateY(-2px); box-shadow: 0 6px 12px rgba(33, 150, 243, 0.3); }
  .checkbox-container { margin: 15px 0; display: flex; align-items: center; gap: 12px; padding: 12px; background: #f8f9fa; border-radius: 6px; }
  .checkbox-container input[type="checkbox"] { width: 18px; height: 18px; cursor: pointer; }
  .checkbox-container label { cursor: pointer; font-weight: 500; }
  .location-status { font-size: 13px; color: #666; padding: 4px 8px; border-radius: 4px; background: #f0f0f0; }
  .location-success { color: white; background: #4CAF50; }
  .location-error { color: white; background: #f44336; }
  .places-container { background: #f8f9fa; border-radius: 8px; padding: 15px; max-height: 350px; overflow-y: auto; }
  .place-item { border: 2px solid #e0e0e0; padding: 12px 14px; border-radius: 8px; margin: 8px 0; cursor: move; background: white; display: flex; align-items: center; transition: all 0.2s ease; }
  .place-item:hover { border-color: #667eea; background: #f9f9ff; }
  .place-item.dragging { opacity: 0.6; background: #e8eaf6; border-color: #667eea; }
  .drag-handle { cursor: move; margin-right: 12px; color: #999; font-size: 18px; }
  .place-name { flex: 1; }
  #desc { margin-top: 20px; padding: 15px; font-size: 14px; border: 1px solid #e0e0e0; border-radius: 8px; background: #fafbfc; line-height: 1.6; }
  #desc b { color: #667eea; }
  .places-container::-webkit-scrollbar { width: 6px; }
  .places-container::-webkit-scrollbar-track { background: #f1f1f1; border-radius: 10px; }
  .places-container::-webkit-scrollbar-thumb { background: #888; border-radius: 10px; }
  .places-container::-webkit-scrollbar-thumb:hover { background: #555; }
</style>
<script src="https://api-maps.yandex.ru/2.1/?apikey={{api_key}}&lang=ru_RU"></script>
</head>

<body>
  <div class="header">
    <h1>🗺️ Туристический маршрут</h1>
    <p>Пермский край — путешествие по достопримечательностям</p>
  </div>
  
  <div id="map"></div>

  <div class="controls">
    <div class="button-group">
      <button id="detect-location">📍 Определить мое местоположение</button>
      <button id="build_route">🗺️ Построить маршрут</button>
    </div>

    <div class="checkbox-container">
      <input type="checkbox" id="start-from-me">
      <label for="start-from-me">Начать маршрут от моей позиции</label>
      <span id="location-status" class="location-status"></span>
    </div>

    <h3>📍 Точки маршрута</h3>
    <p style="font-size: 12px; color: #999; margin-bottom: 12px;">Перетащите пункты для изменения порядка</p>
    <div class="places-container" id="places_list"></div>

    <div id="desc"><i style="color: #999;">👇 Нажмите на место, чтобы увидеть описание</i></div>
  </div>

<script>
ymaps.ready(init);

function init() {
  // 📍 Заданные точки маршрута
  let PLACES = [
    { name: "Кунгурская ледяная пещера", coords: [57.4267, 56.9562], desc: "Одна из самых известных карстовых пещер России." },
    { name: "12 — смотровая площадка", coords: [58.2905, 57.8192], desc: "Живописный вид на реку Чусовую." },
    { name: "12 — смотровая площадка", coords: [48.2905, 57.8192], desc: "Живописный вид на реку Чусовую." },
    { name: "Пермь — Набережная Камы", coords: [58.0105, 56.2502], desc: "Центральная набережная города Перми." }
  ];

  let map = new ymaps.Map("map", { center: [57.8, 56.5], zoom: 7 });
  let currentRoute = null;
  let myLocation = null;
  let myLocationMarker = null;

  // Функция для обновления маркеров на карте
  function updateMapMarkers() {
    // Сохраняем текущие маркеры
    let savedMarkers = [];
    if (myLocationMarker) {
      savedMarkers.push(myLocationMarker);
    }
    
    // Удаляем все маркеры
    map.geoObjects.removeAll();
    
    // Добавляем сохраненный маркер местоположения
    savedMarkers.forEach(marker => map.geoObjects.add(marker));
    
    // Добавляем новые POI метки на карту с актуальным порядком
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
      div.innerHTML = `<span class="drag-handle">⋮⋮</span><span class="place-name">${i + 1}. ${p.name}</span>`;
      
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
