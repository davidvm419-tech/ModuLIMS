from django.db import models
from django.conf import settings


ASSAY_CATEGORIES = [
    ('MICROBIOLOGY', 'Microbiología'),
    ('PHYSICOCHEMICAL', 'Fisicoquímico'),
]

class Assay(models.Model):
    name = models.CharField('Ensayo', max_length=100)
    category = models.CharField('Categoria',  choices=ASSAY_CATEGORIES, default='MICROBIOLOGY', max_length=25)
    specification = models.CharField('Especificación', max_length=100)
    units = models.CharField('Unidades', max_length=100)
    methodology = models.CharField('Metodología',max_length=50)
    normative_reference = models.CharField('Referencia normativa',max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'ensayos'

    def __str__(self):
        return f"{self.name}-{self.specification}"


class AssayTraceability(models.Model):
    assay = models.ForeignKey(Assay, on_delete=models.CASCADE, related_name='traceability_logs')
    user_responsible = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sample_actions_logged')
    event = models.TextField('Evento')
    event_date = models.DateTimeField('Fecha', auto_now_add=True)

    class Meta:
        ordering = ['-event_date']
        verbose_name = 'Trazabilidad de la muestra'


class SampleAssay(models.Model):
    sample = models.ForeignKey('samples.Sample', on_delete=models.CASCADE, related_name='sample_assays')
    assay = models.ForeignKey(Assay, on_delete=models.CASCADE, related_name='sample_assays')

class Meta:
    verbose_name = 'ensayos de muestra'
    