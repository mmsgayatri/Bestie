import requests

city_name = 'Vijayawada'
API_Key = '2ad189e85c6980a11a12747acd9dfa58'
url = f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_Key}&units=metric'

response = requests.get(url)

if response.status_code == 200:
    store = response.json()
    print('Weather update in ',city_name,'is',store['weather'][0]['description'])
    print('Humidity :', store['main']['humidity'])
    print('Temperature :',store['main']['temp'])
    print('Current temperature feels like :', store['main']['feels_like'])
