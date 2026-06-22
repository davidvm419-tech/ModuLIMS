from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import User, UserTraceability
from .test_data import UserBaseAdminData, UserBaseProfileData


# Create your tests here.

class UserAdminAPITestCase(UserBaseAdminData, APITestCase):
    def setUp(self):
        self.admin_user = User.objects.create(
            first_name = 'Peter',
            last_name = 'Admin',
            identification = '12954321789',
            email = 'peter@test.com',
            username = 'peter_admin',
            job_title = 'Coordinador de Labratorio',
            rol = 'LABORATORY COORDINATOR',
            password = 'superpassword123',
        )

        self.client.force_authenticate(user=self.admin_user)

        self.url = reverse('user-administration-list')

    def test_create_valid_user(self):
        data = self.get_valid_user()

        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)