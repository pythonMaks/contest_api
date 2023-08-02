from django.db import models
from django.contrib.auth.models import AbstractUser



class User(AbstractUser):
    uid = models.CharField(("language"), max_length=300, blank=True)

   

                 
           
