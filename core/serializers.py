from rest_framework import serializers
from .models import Task, Test, Submission

class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Test
        fields = ['id', 'input', 'output', 'task']

class TaskSerializer(serializers.ModelSerializer):
    tests = TestSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'language', 'name', 'description', 'created_at', 'updated_at', 'prepod', 'tests']


class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'task', 'code', 'status', 'created_at', 'updated_at', 'student', 'output', 'error']
