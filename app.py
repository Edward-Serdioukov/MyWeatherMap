from flask import Flask, render_template
import folium
import requests
import datetime


app = Flask(__name__)

# Ваш API ключ OpenWeatherMap
API_KEY = "6a9eedc6772205944011d6cbf0b0323f"

# Список городов с их координатами
cities = [
    {'name': 'Milan', 'lat': 45.4642, 'lon': 9.1895}, 
    {'name': 'Prague', 'lat': 50.0878, 'lon': 14.4205}, 
    {'name': 'Marianske Lazne', 'lat': 49.96489, 'lon': 12.7007}, 
    {'name': 'Venezia', 'lat': 45.4944, 'lon': 12.3714}, 
    
    # Добавьте другие города по желанию
]

def get_weather_day(city_name):
    api_key = "6a9eedc6772205944011d6cbf0b0323f"
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    complete_url = f"{base_url}q={city_name}&appid={api_key}"
    
    response = requests.get(complete_url)
    
    if response.status_code == 200:
        data = response.json()
        main = data['main']
        wind = data['wind']
        weather_description = data['weather'][0]['description']
        icon_code = data['weather'][0]['icon']  # Код иконки погоды
        day = datetime.datetime.fromtimestamp(data['dt']).strftime('%A')
        
        
        # Преобразуем температуру в градусы Цельсия
        temperature_celsius = main['temp'] - 273.15
        
        # Преобразуем давление в мм рт. ст.
        pressure_mm_hg = main['pressure'] * 0.75006375541921
        
        return {
            'day': day,
            'city': city_name,
            'temperature': round(temperature_celsius, 2),
            'pressure': round(pressure_mm_hg, 2),
            'humidity': main['humidity'],
            'wind_speed': wind['speed'],
            'description': weather_description,
            'icon': f"http://openweathermap.org/img/wn/{icon_code}@2x.png"  # URL иконки
        }
    else:
        return None

def get_weather_week(city_name):
    api_key = "6a9eedc6772205944011d6cbf0b0323f"
    geocoding_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city_name}&appid={api_key}"
    geo_response = requests.get(geocoding_url)

    if geo_response.status_code == 200:
        geo_data = geo_response.json()
        if len(geo_data) == 0:
            return None
        
        lat = geo_data[0]['lat']
        lon = geo_data[0]['lon']
        
        weather_url = f"http://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=current,minutely,hourly,alerts&appid={api_key}"
        response = requests.get(weather_url)
        
        if response.status_code == 200:
            data = response.json()
            daily_forecast = []
            
            for day in data['daily']:
                # Преобразование метки времени в день недели
                day_name = datetime.datetime.fromtimestamp(day['dt']).strftime('%A')
                
                daily_forecast.append({
                    'day': day_name,  # Передаем уже отформатированное имя дня
                    'temperature': day['temp']['day'] - 273.15,
                    'pressure': day['pressure'] * 0.75006375541921,
                    'humidity': day['humidity'],
                    'wind_speed': day['wind_speed'],
                    'description': day['weather'][0]['description'],
                    'icon': f"http://openweathermap.org/img/wn/{day['weather'][0]['icon']}@2x.png"
                })
            
            return daily_forecast
        else:
            return None
    else:
        return None

  
@app.route('/')
def index():
    # Создаем карту

    folium_map = folium.Map(location=[48.0, 18.0], zoom_start=5)
    folium_map.get_root().header.add_child(folium.CssLink('/static/css/style.css'))
    
    for city in cities:
        # Получаем данные о погоде
        ###weather_today, weather_week = get_weather(city['lat'], city['lon'])
        #weather_today = get_weather_day(city['name'])
        # Создаем всплывающее окно с прогнозом на неделю
        #popup_html += f"<img src='{weather_today['icon']}'><br>"
        #popup_html += f"{weather_today['temperature']}°C, {weather_today['description']}<br>"
        
        weather_week = get_weather_week(city['name'])
        if weather_week:
            # Начинаем строить HTML для попапа
            popup_html = f"<b>{city['name']}</b><br>"
            popup_html += "<table border='1' style='width: 100%; border-collapse: collapse;'>"
            
            # Добавляем три столбца, каждый из которых будет содержать три строки с данными
            popup_html += "<tr>"

            # Разбиваем погоду по дням на 3 столбца
            for i in range(3):
                popup_html += "<td style='padding: 10px; vertical-align: top;'>"
                
                # В каждом столбце — три строки (по одному дню)
                for j in range(3):
                    day_index = i * 3 + j
                    if day_index < len(weather_week):
                        day = weather_week[day_index]
                        popup_html += f"<div style='margin-bottom: 10px;'>"
                        popup_html += f"<b>{day['day']}</b><br>"
                        popup_html += f"<img src='{day['icon']}'><br>"
                        popup_html += f"<b>{round(day['temperature'], 1)}°C</b><br>"
                        popup_html += f"<i>{day['description']}</i><br>"
                        popup_html += "</div>"
                
                popup_html += "</td>"

            popup_html += "</tr></table>"
        
        # Добавляем маркер на карту
        folium.Marker(
            location=(city['lat'], city['lon']),
            popup=popup_html,
            #icon=folium.DivIcon(html=f"""<div style="font-family: courier new; color: red; font-weight: bold">{city['name']}, {weather_today['temperature']}°C</div>"""),
            tooltip=f"{city['name']}: {weather_week[0]['day']}, {round(weather_week[0]['temperature'])}°C, {weather_week[0]['description']}"
        ).add_to(folium_map)
        

    folium_map.save('static/map.html')
    return render_template('index.html',  title="My Weather Map", map_url='map.html')



if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=int(os.environ.get("PORT", 3000)))
    #app.run(debug=True)
    app.run(host='0.0.0.0', port=8080, debug=True)
