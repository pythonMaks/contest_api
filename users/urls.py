from django.urls import path
from .views import MyAPIView

urlpatterns = [
    path('my-api/', MyAPIView.as_view()),
    # ...
]
