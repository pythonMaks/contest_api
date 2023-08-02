from django.urls import path
from .views import TaskListCreate, TestListCreate, TaskDetail, TestDetail, SubmissionCreateView, SubmissionListView, StudentSubmissionListView

urlpatterns = [
    path('tasks/', TaskListCreate.as_view(), name='task-list-create'),
    path('tests/', TestListCreate.as_view(), name='test-list-create'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('tests/<int:pk>/', TestDetail.as_view(), name='test-detail'),
    path('submission/', SubmissionCreateView.as_view(), name='submission-create'),
    path('submissions/', SubmissionListView.as_view(), name='submission-list'),
    path('submissions/<str:uid>/', StudentSubmissionListView.as_view(), name='student-submission-list'),
    path('tasks/', TaskListCreate.as_view(), name='task-list'),
    path('tasks/<int:pk>/', TaskDetail.as_view(), name='task-detail'),
    path('tasks/<int:task_id>/tests/', TestListCreate.as_view(), name='task-tests'),
    path('tests/<int:pk>/', TestDetail.as_view(), name='test-detail'),
]
