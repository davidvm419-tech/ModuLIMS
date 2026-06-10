from django.db import models

# Create your models here.

class Client(models.Model):
    name = models.CharField(max_length=100)
    contact = models.CharField(max_length=100)
    email = models.CharField(max_length=50)
    phone = models.CharField(max_length=20)
    adress = models.CharField(max_length=100)  



