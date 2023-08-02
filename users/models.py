from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    uid = models.CharField(max_length=300, blank=True)
    
    def __str__(self):
        return self.uid

   

                 
           
