from django.db import models
from django.conf import settings

class Client(models.Model):
    name = models.CharField('Cliente', max_length=100,  unique=True)
    nit = models.CharField('NIT', max_length=100, unique=True)
    address = models.CharField('Dirección', max_length=100)
    contact_person = models.CharField('Contacto', max_length=100)
    email = models.CharField('Correo electrónico', max_length=50)
    phone = models.CharField('Teléfono', max_length=20)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

    def __str__(self):
        return self.name


class ClientTraceability(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name="traceability_logs")
    user_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="client_actions_logged")
    event = models.TextField('Evento')
    event_date = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Trazabilidad de clientes'
