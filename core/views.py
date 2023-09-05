from rest_framework import generics, status
from .models import Task, Test
from .serializers import TaskSerializer, TestSerializer, SubmissionSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import chardet
import shlex
import docker
from .models import Submission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from firebase_admin import auth, credentials
from rest_framework.permissions import IsAuthenticated


class TaskListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    
    prepod_uid_param = openapi.Parameter(
        'prepod_uid', 
        openapi.IN_QUERY,
        description="UID преподавателя, для которого будут возвращены задачи.",
        type=openapi.TYPE_STRING
    )

    @swagger_auto_schema(manual_parameters=[prepod_uid_param], operation_description="Возвращает список всех задач или задач определенного препода.")
    def get_queryset(self):
        """
        Возможность просмотра списка всех задач или задач определенного препода.
        """
        prepod_uid = self.request.query_params.get('prepod_uid', None)
        if prepod_uid is not None:
            return Task.objects.filter(prepod_uid=prepod_uid)
        else:
            return Task.objects.all()
    @swagger_auto_schema(operation_description="Создает новую задачу.")
    def perform_create(self, serializer):
        serializer.save(prepod_uid=self.request.user.uid)


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Task.objects.all()
    serializer_class = TaskSerializer


class TestListCreate(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TestSerializer
    @swagger_auto_schema(operation_description="Возвращает тесты, связанные с конкретной задачей.")
    def get_queryset(self):
        """
        Возвращает тесты, связанные с конкретной задачей.
        """
        task_id = self.kwargs['task_id']
        return Test.objects.filter(task_id=task_id)


class TestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

@swagger_auto_schema(operation_description="Возвращает список всех решений.")
class SubmissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    """
    Возвращает список всех решений.
    """
    queryset = Submission.objects.all()
    serializer_class = SubmissionSerializer
    

@swagger_auto_schema(operation_description="Возвращает список решений конкретного студента.")
class StudentSubmissionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    """
    Возвращает список решений конкретного студента.
    """
    
    serializer_class = SubmissionSerializer
    @swagger_auto_schema(operation_description="Возвращает список решений конкретного студента.")
    def get_queryset(self):
        """
        Фильтрует решения по uid студента.
        """
        student_uid = self.kwargs['uid']
        return Submission.objects.filter(student_uid=student_uid)

class SubmissionCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, format=None):
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
            serializer = SubmissionSerializer(data=request.data)
            if serializer.is_valid():
                submission = serializer.save(student_uid=uid) # теперь используем UID пользователя
                self.process_submission(submission, uid)

                return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'No token provided'}, status=status.HTTP_401_UNAUTHORIZED)

    # остальная часть вашего кода

    def process_submission(self, submission, user):
        task = submission.task

        test_cases = Test.objects.filter(task=task)  # получение всех тестов для этого задания                                
        passed = []   
        error = [] 
        output = []

        for test_case in test_cases:
            output_i, error_i, pass_flag = self.process_test_case(test_case, submission, task, user)
            output.append(output_i)
            error.append(error_i)
            passed.append(pass_flag)

        if False in passed:
            passed = False
        for i in error:
            if i:
                error = i.strip()  
                break                 
        else:
            error = ''

        if error:
            submission.status = 'E'
        elif passed:
            submission.status = 'AC'
        else:
            submission.status = 'WA'

        submission.save()

    def process_test_case(self, test_case, submission, task, user):
        input_data = test_case.input.strip()
        expected_output = test_case.output.strip()
        output_i, error_i, pass_flag = None, None, None

        if input_data and expected_output:   
            output_i, error_i = execute_code(submission.code, task.language, input_data, user, expected_output)
            try:              
                if isinstance(output_i, bytes):
                    encoding = chardet.detect(output_i)['encoding']
                    output_i = output_i.decode(encoding).strip()
                pass_flag = output_i.splitlines() == expected_output.strip().splitlines()
                submission.output.append(output_i)  # обновление поля output
            except Exception as e:
                if isinstance(error_i, bytes):
                    encoding = chardet.detect(error_i)['encoding']
                    try:
                        error_i = error_i.decode(encoding).strip()
                    except:
                        pass
                submission.error.append(error_i)  # обновление поля error

        return output_i, error_i, pass_flag
    
    
def execute_code(code, language, input_data, user, expected_output=None):
    if 'import' in code:
        return 'Import forbidden', ''
    client = docker.from_env()
    
    volume_name = user
    try:
        volume = client.volumes.get(volume_name)
    except docker.errors.NotFound:
        volume = client.volumes.create(volume_name)

    image_name = 'pythonmaks/contest'

    if language == 'python':
        code_command = f'python3 -c {shlex.quote(f"""{code}""")} < /code/input.txt'
    elif language == 'java':
        code_command = (f'echo {shlex.quote(code)} > /code/Main.java && '
                        f'javac /code/Main.java && '
                        f'java -cp /code Main < /code/input.txt')
    elif language == 'node':
        if input_data.startswith('[') and input_data.endswith(']'):
            input_arg = f"JSON.parse({shlex.quote(input_data)})"
        elif input_data.startswith('"') and input_data.endswith('"'):
            input_arg = shlex.quote(input_data)
        else:
            # Попытка интерпретировать как число
            try:
                float(input_data)  # Проверка, является ли строка числом
                input_arg = input_data
            except ValueError:
                raise ValueError(f"Unsupported input format: {input_data}")
                
        execution_code = (
            f"{code}"
            f"const inputData = {input_arg};"
            f"const result = Main(inputData);"  # замените 'yourFunctionName' на имя вашей функции
            "console.log(JSON.stringify(result));"
        )
        code_command = f'node -e {shlex.quote(execution_code)}'
    
        

    elif language == 'kotlinc':
        code_command = (f'echo {shlex.quote(code)} > /code/Main.kt && '
                        f'kotlinc /code/Main.kt -include-runtime -d /code/main.jar && '
                        f'java -jar /code/main.jar < /code/input.txt')

    else:
        raise ValueError(f'Unsupported language: {language}')

    input_data_command = f'{code_command}; rm -rf /code/*'


    container = client.containers.run(image_name,
                                      volumes={volume_name: {'bind': '/code', 'mode': 'rw'}},
                                      command=['/bin/sh', '-c', input_data_command],
                                      detach=True, working_dir="/code")

    container.wait()
    #logger = logging.getLogger(__name__)
    #logger.info(volume)
    stdout = container.logs(stdout=True, stderr=False)
    stderr = container.logs(stdout=False, stderr=True)

    container.remove()

    if stdout:
        if isinstance(stdout, bytes):
            stdout_encoding = chardet.detect(stdout)['encoding']
            stdout = stdout.decode(stdout_encoding).strip()

    if stderr:
        if isinstance(stderr, bytes):
            stderr_encoding = chardet.detect(stderr)['encoding']
            stderr = stderr.decode(stderr_encoding).strip()
        #logger.info(stderr)

    return stdout, stderr
