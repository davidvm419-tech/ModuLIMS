from django.db import models
from django.conf import settings


class SampleType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    prefix = models.CharField(max_length=10, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Tipo de muestra'
        verbose_name_plural = 'Tipo de muestras'
    
    def __str__(self):
        return self.name
    

SAMPLE_STATUS = [
    ('RECEIVED', 'Recibido'),
    ('TESTING', 'En análisis'),
    ('REVISION', 'En revisión'),
    ('APPROVAL', 'En aprobación'),
    ('ENDED', 'Finalizado'),
]


class Sample(models.Model):
    client = models.ForeignKey('clients.Client', on_delete=models.CASCADE, related_name='samples')
    code = models.CharField('código', max_length=50, blank=True, unique=True)
    name = models.CharField('Nombre', max_length=100)
    type = models.ForeignKey(SampleType, on_delete=models.CASCADE, related_name='samples')
    manufacturing_date = models.DateField('Fecha de fabricación')
    expiration_date = models.DateField('Fecha de vencimiento')
    description = models.TextField('Descripción')
    quantity = models.CharField('Cantidad de muestra', max_length=100)
    observations = models.TextField('Observaciones')
    received_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField('Estado', choices=SAMPLE_STATUS, default='RECEIVED', max_length=25)    
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-received_date']
        verbose_name = 'Muestra'
        verbose_name_plural = 'Muestras'

    def __str__(self):
        return f"{self.code}-{self.name}"


class SampleTraceability(models.Model):
    sample = models.ForeignKey(Sample, on_delete=models.CASCADE, related_name='traceability_logs')
    user_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sample_actions_logged')
    event = models.TextField('Evento')
    event_date = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Trazabilidad de la muestra'
