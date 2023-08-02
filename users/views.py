from django.contrib.auth import get_user_model
import firebase_admin
from firebase_admin import auth, credentials
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

cred = credentials.Certificate('contest-api-a0502-firebase-adminsdk-tndsy-840e956564.json')
firebase_admin.initialize_app(cred)

User = get_user_model()

class MyAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # получаем токен из заголовков запроса
        id_token = request.META.get('HTTP_AUTHORIZATION')
        if id_token:
            # убираем префикс "Bearer " из заголовка
            id_token = id_token[7:]
            try:
                # проверяем токен с помощью SDK Firebase Admin
                decoded_token = auth.verify_id_token(id_token)
            except ValueError:
                # Если токен недействителен, возвращаем ошибку 401
                return Response({'error': 'Invalid token'}, status=status.HTTP_401_UNAUTHORIZED)
                
            uid = decoded_token['uid']
            # получаем пользователя из базы данных Django, или создаем нового, если не найдено
            user, created = User.objects.get_or_create(uid=uid, defaults={'username': uid})
            # здесь вы можете выполнить дополнительную логику, если пользователь был только что создан
            if created:
                # например, устанавливаем email пользователя
                user.email = decoded_token['email']
                user.save()
            # продолжаем обработку запроса
            # ...
        else:
            return Response({'error': 'No token provided'}, status=status.HTTP_401_UNAUTHORIZED)

