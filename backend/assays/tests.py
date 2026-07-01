from django.contrib.auth import get_user_model # django will get the custom user model when defined
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Assay,  AssayTraceability, SampleAssay
from clients.models import Client
from .test_data import AssayBaseData, SampleAssayBaseData


User = get_user_model()


class AssayAPITestCase(AssayBaseData, APITestCase):
    """
    test the assay views endpoints to create, update and "delete" any assay.
    And retreive sample traceability logs.
    """