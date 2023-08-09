from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
import firebase_admin
from firebase_admin import auth, credentials

# Инициализация Firebase Admin SDK
cred = credentials.Certificate('gamification-447b4-firebase-adminsdk-6l7sw-bf895158b2.json')
default_app = firebase_admin.initialize_app(cred)

class FirebaseAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return None

        # убираем префикс "Bearer " из заголовка
        id_token = auth_header.split(' ')[1]
        try:
            # проверяем токен с помощью SDK Firebase Admin
            decoded_token = auth.verify_id_token(id_token)
        except ValueError:
            # Если токен недействителен, выбрасываем исключение
            raise exceptions.AuthenticationFailed('Invalid token')

        return (self.get_user(decoded_token), None)

    def get_user(self, decoded_token):
        uid = decoded_token['uid']
        return uid
