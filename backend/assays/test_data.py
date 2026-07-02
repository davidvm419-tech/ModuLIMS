from django.core.files.uploadedfile import SimpleUploadedFile
import io
from PIL import Image
from rest_framework.test import APITestCase


class AssayBaseData(APITestCase):
    """
    base class to create the test data when 
    creating, updating or inactivating assays.
    """
    def get_valid_assay1(self):
        return {
            'name' : 'Recuento de microorganismos mesfilos aerobios',
            'category' : 'MICROBIOLOGY',
            'methodology' : 'pos-m-001',
            'normative_reference' : 'USP NF 61',
        }

    def get_valid_assay2(self):
        return {
            'name' : 'Recuento de Hongos y  levaduras',
            'category' : 'MICROBIOLOGY',
            'methodology' : 'pos-m-002',
            'normative_reference' : 'USP NF 61',
        }

    def get_inactive_assay(self):
        return {
            'name' : 'Análisis de coliformes totales',
            'category' : 'MICROBIOLOGY',
            'methodology' : 'pos-m-007',
            'normative_reference' : 'Método interno',
            'is_active' : False,
        }

    def get_duplicated_assay(self):
        return {
            'name' : 'Detección de Escherichia coli',
            'category' : 'MICROBIOLOGY',
            'methodology' : 'pos-m-002',
            'normative_reference' : 'USP NF 61',
        }

    def get_create_invalid_assay(self):
        return {
            'name' : 'Detección de Escherichia coli',
            'category' : 'MICROBIOLOGY',
            'methodology' : '',
            'normative_reference' : '',
        }

    def get_update_valid_assay(self):
        return {
            'methodology' : 'pos-m-012',
            'justification' : 'Actualización de metodología.',
        }

    def get_update_invalid_assay(self):
        return {
            'methodology' : 'pos-m-012',
        }

    def get_destroy_valid_assay(self):
        return {
            'justification' : 'Se inactiva el análisis de recuento por actualización  normativa.'
        }

    def get_destroy_invalid_assay(self):
        return {}


class SampleAssayBaseData(APITestCase):
    """
    base class to create the test data when 
    updating or deleting sample assays.
    """
    def get_update_valid_sample_assay(self):
        return {
            'specification' : '<=500',
            'justification' : 'Actualización de especificación por error del cliente.',
        }

    def get_update_invalid_sample_assay(self):
        return {
            'specification' : '<=500',
        }

    def get_destroy_valid_sample_assay(self):
        return {
            'justification' : 'Se elimina el análisis de hongos y levaduras por solicitud del cliente.'
        }

    def get_destroy_invalid_sample_assay(self):
        return {}
