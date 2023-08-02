from django.db import models


class Task(models.Model): 
    language = models.CharField(("language"), max_length=150, blank=True)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField()    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    prepod_uid = models.CharField(max_length=150)

        
    def __str__(self):
        return self.name           
    
    
    def get_language(self):
        LANGUAGE_CHOICES = {
        'python': 'Python',
        'kotlinc': 'Kotlin',
        'node': 'JavaScript',
        'java': 'Java',
        }
        return LANGUAGE_CHOICES.get(self.language)

        
class Test(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    input = models.TextField()
    output = models.TextField()
    def __str__(self):
        return self.task.name   


class Submission(models.Model): 
    STATUS_CHOICES = (       
        ('AC', 'Успешно'),
        ('WA', 'Неправильный вывод'),        
        ('E', 'Ошибка'),
    )

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    code = models.TextField()
    status = models.CharField(max_length=3, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    student_uid = models.CharField(max_length=150)
    output = models.JSONField(default=list, blank=True)
    error = models.JSONField(default=list, blank=True)
    def __str__(self):
        return f'{self.id} - {self.task.name} - {self.get_status_display()}'

    