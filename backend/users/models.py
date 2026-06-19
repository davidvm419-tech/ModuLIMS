from django.contrib.auth.models import AbstractUser
from django.db import models

# Create your models here.
LABORATORY_ROLES = [
    ('ASSISTANT', 'Asistente técnico'),
    ('AUXILIARY', 'Auxiliar'),
    ('LABORATORY ANALYST', 'Analista de Laboratorio'),
    ('QUALITY_ANALYST', 'Analista de Calidad'),
    ('LABORATORY COORDINATOR', 'Coordinador de Laboratorio'),
    ('QUALITY CHIEF', 'Jefe de Calidad'),
    ('DIRECTOR', 'Director de Laboratorio'),
    ('ADMINISTRATOR', 'Administrador de Sistema'),
]

class User(AbstractUser):
    first_name = models.CharField('Nombre(s)', max_length=50)
    last_name = models.CharField('Apellido(s)', max_length=50)
    identification = models.CharField('Cédula', max_length=50, unique=True)
    email = models.EmailField('correo', max_length=50)
    username = models.CharField('Nombre de usuario', max_length=80, unique=True)
    job_title = models.CharField('Cargo', max_length=80)
    rol = models.CharField('Rol', choices=LABORATORY_ROLES, default='ASSISTANT')
    sign = models.ImageField('Firma BPD', blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['first_name']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class UserTraceability(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="traceability_logs")
    user_responsible = models.ForeignKey(User,  on_delete=models.CASCADE, related_name="actions_logged")
    event = models.TextField('Evento')
    event_date = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Trazabilidad de usuarios'
