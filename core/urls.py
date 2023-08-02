from django.urls import path
from .views import TaskListCreate, TestListCreate, TaskDetail, TestDetail, SubmissionCreateView

urlpatterns = [
    path('tasks/', TaskListCreate.as_view(), name='task-list-create'),
    path('tests/', TestListCreate.as_view(), name='test-list-create'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('tests/<int:pk>/', TestDetail.as_view(), name='test-detail'),
    path('submission/', SubmissionCreateView.as_view(), name='submission-create'),
]
