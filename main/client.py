import requests

# Отправка запроса на логин и получение токена
login_data = {
    'username': 'rametov',
    'password': '123'
}
response = requests.post('http://127.0.0.1:8000/login/', data=login_data)
token = response.json()['token']

# Использование токена для доступа к защищенным эндпоинтам
headers = {
    'Authorization': f'Token {token}',
}
response = requests.get('http://127.0.0.1:8000/tasks/', headers=headers)
