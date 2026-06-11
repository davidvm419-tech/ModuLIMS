from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Client(models.Model):
    name = models.CharField('Cliente', max_length=100)
    nit = models.CharField('NIT', max_length=100)
    address = models.CharField('Dirección', max_length=100)
    contact_person = models.CharField('Contacto', max_length=100)
    email = models.CharField('Correo electrónico', max_length=50)
    phone = models.CharField('Teléfono', max_length=20)

    class Meta:
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name



class SampleCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    code_prefix = models.CharField(max_length=10, unique=True)


    class Meta:
        ordering = ['name']
        verbose_name = 'Categoria de muestra'
        verbose_name_plural = 'Categoria de muestras'
    
    def __str__(self):
        return self.name


class Sample(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='samples')
    code = models.CharField('código', max_length=50, blank=True, unique=True)
    name = models.CharField('Nombre', max_length=100)
    sample_type = models.ForeignKey(SampleCategory, on_delete=models.CASCADE, related_name='samples')
    manufacturing_date = models.DateField('Fecha de fabricación')
    expiration_date = models.DateField('Fecha de vencimiento')
    description = models.CharField('Descripción', max_length=500)
    quantity = models.CharField('Cantidad de muestra', max_length=100)
    observations = models.CharField('Observaciones', max_length=500)
    received_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Muestra'
        verbose_name_plural = 'Muestras'

    def __str__(self):
        return f"{self.code}-{self.name}"


class SampleTraceability(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='traceability_logs')
    user_responsible = models.ForeignKey(User, on_delete=models.CASCADE, related_name='actions_logged')
    event = models.CharField('Evento', max_length=100)
    time = models.DateTimeField('Hora', auto_now_add=True)

    class Meta:
        verbose_name = 'Trazabilidad de la muestra'
        ordering = ['-time']
