from rest_framework import generics, status
from .models import Task, Test
from .serializers import TaskSerializer, TestSerializer, SubmissionSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
import chardet
import shlex
import docker

class TaskListCreate(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TestListCreate(generics.ListCreateAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer

class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

class TestDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Test.objects.all()
    serializer_class = TestSerializer



class SubmissionCreateView(APIView):
    def post(self, request, format=None):
        serializer = SubmissionSerializer(data=request.data)
        if serializer.is_valid():
            submission = serializer.save(student=request.user)
            # Обработка кода и тестов, а также сохранение результатов
            self.process_submission(submission, request.user)

            return Response(SubmissionSerializer(submission).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def process_submission(self, submission, user):
        task = submission.task
        submission.prepod = submission.task.prepod

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
            output_i, error_i = execute_code(submission.code, task.language, input_data, user.username)
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
    
    
def execute_code(code, language, input_data, user):
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
        code_command = f'node -e {shlex.quote(code)} < /code/input.txt'
    elif language == 'kotlinc':
        code_command = (f'echo {shlex.quote(code)} > /code/Main.kt && '
                        f'kotlinc /code/Main.kt -include-runtime -d /code/main.jar && '
                        f'java -jar /code/main.jar < /code/input.txt')

    else:
        raise ValueError(f'Unsupported language: {language}')

    input_data_command = f'echo {shlex.quote(input_data)} > /code/input.txt; {code_command}; rm -rf /code/*'

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
