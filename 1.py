# import firebase_admin
# from firebase_admin import auth, credentials

# cred = credentials.Certificate('contest-api-a0502-firebase-adminsdk-tndsy-840e956564.json')


# # Инициализируем Firebase Admin SDK.
# default_app = firebase_admin.initialize_app(cred)

# # Создаем нового пользователя.
# user = auth.create_user(
#     email='useer@example.com',
#     email_verified=False,
#     password='myepassword',
# )

# print('User created: {0}'.format(user.uid))

# # Получаем токен ID для созданного пользователя
# custom_token = auth.create_custom_token(user.uid)
# print('Generated custom token: {0}'.format(custom_token))




# import requests
# custom_token = b'eyJhbGciOiAiUlMyNTYiLCAidHlwIjogIkpXVCIsICJraWQiOiAiODQwZTk1NjU2NDY3NzdhNzllNmYxNGJiZDUwMzYzZjYzZGI1YzdjYSJ9.eyJpc3MiOiAiZmlyZWJhc2UtYWRtaW5zZGstdG5kc3lAY29udGVzdC1hcGktYTA1MDIuaWFtLmdzZXJ2aWNlYWNjb3VudC5jb20iLCAic3ViIjogImZpcmViYXNlLWFkbWluc2RrLXRuZHN5QGNvbnRlc3QtYXBpLWEwNTAyLmlhbS5nc2VydmljZWFjY291bnQuY29tIiwgImF1ZCI6ICJodHRwczovL2lkZW50aXR5dG9vbGtpdC5nb29nbGVhcGlzLmNvbS9nb29nbGUuaWRlbnRpdHkuaWRlbnRpdHl0b29sa2l0LnYxLklkZW50aXR5VG9vbGtpdCIsICJ1aWQiOiAiV3hlR1pYNkpCU1pBRXVKamNwV0NUMjY3djdBMyIsICJpYXQiOiAxNjkwOTU1NzA2LCAiZXhwIjogMTY5MDk1OTMwNn0.0R-nadPnYYY-59CzZe4aHmGHkUEMmnsoL2SsLfpNPL6PAyqgGF9WEC6UtARaJMJuXQoJbeGa4-FznvczDk1TzilmaFvUln08FiAIdJMsM-ICaZcBpXo_Kd0KQzg1W1E_5GpoVNUojLIUCyzS3naFAS15T6XeJtMZmHsjfCQXLPOTqjUuTeX9NEPQmuoOgNRASLfqxPlO4o1H9y82txXMbPyBLIFlGRUg3PjUpdzw39-8pazKOoQxMZjaBgWAy_JzlfVDghQvYBKDFVNsey2xwqfNgmFxZyqa3yp54UQAh1GP7j8uRrurbnKjmbRboRNTarFnjyv4llgb3S02xk7IFw'.decode("utf-8")

# url = "http://localhost:8000/my-api/"
# headers = {
#     "Authorization": f"Bearer {custom_token}"
# }

# response = requests.get(url, headers=headers)

# print(response.status_code)
# print(response.text)
import requests
import json

# URL вашего API
url = "http://16.16.142.16:8000/api/submission/"  # Замените на ваш URL

# Данные, которые вы хотите отправить
data = {
    "student": 1,  # Замените на данные вашего студента
    "task": 1,  # Замените на данные вашего задания
    "code": "print(1)",  # Замените на пример кода
    "language": "python",  # Замените на язык программирования
}

# Если вам требуется аутентификация, вы можете включить ее так:
headers = {
    "Content-Type": "application/json",  # Замените на ваш токен
    "Authorization": "Token a0b301b87fc501ae630d4954b7d4d63bf0073cd8"
}

# Отправка POST-запроса
response = requests.post(url, headers=headers, data=json.dumps(data))

# Вывод ответа сервера
if response.content:
    print(response.content)
else:
    print("Ответ не содержит содержимого")

# Попытка преобразования ответа в JSON только если ответ содержит контент
if response.content:
    try:
        print(response.json())
    except requests.exceptions.JSONDecodeError:
        print("Не удалось декодировать ответ в JSON")