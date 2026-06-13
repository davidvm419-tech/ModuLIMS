from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Client

# Create your tests here.
class ClientAPITestCase(APITestCase):
    def setUp(self):
        '''
        test data for client views
        '''  
        self.active_client  = Client.objects.create(
            name = 'LABORATORIO A',
            nit = '540.211.322.562.2',
            address = 'calle real 435 # 11-41',
            contact_person = 'John Doe',
            email = 'alfa@email.com',
            phone = '310 412 5412',
            is_active = True,
        )

        self.inactive_client  = Client.objects.create(
            name = 'LABORATORIO F',
            nit = '120.511.411.132.1',
            address = 'calle falsa 123 # 37-11',
            contact_person = 'False Doe',
            email = 'falso@email.com',
            phone = '301 312 3151',
            is_active = False,
        )

        self.list_url = reverse('client-list')
        self.detail_url = reverse('client-detail', kwargs={'pk': self.active_client.pk})

    def test_list_active_clients(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'LABORATORIO A')    

    def test_create_valid_client(self):
        data = {
            'name' : 'Laboratorio C',
            'nit' : '121.430.223.111',
            'address' : 'calle 45 # 1-1',
            'contact_person' : 'Pepe Real',
            'email' : 'c@email.com',
            'phone' : '301 322 311',
            'is_active' : True,
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_201_CREATED)
        self.assertTrue(Client.objects.filter(nit='121.430.223.111').exists())      

    def test_create_invalid_client(self):
        data = {
            'name' : 'laboratorio a',
            'nit' : '123.433.223.111',
            'address' : 'calle 51 # 2-1',
            'contact_person' : 'Many Ice',
            'email' : 'm@email.com',
            'phone' : '312 412 4321',
            'is_active' : True,
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_retrieve_client(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['address'], 'calle real 435 # 11-41')

    def test_update_client_put(self):
        data = {
            'name' : 'LABORATORIO A ACTUALIZADO',
            'nit' : '540.212.322.562.2',
            'address' : 'calle real nueva 435 # 11-41',
            'contact_person' : 'John Doe jr',
            'email' : 'alfa_nuevo@email.com',
            'phone' : '310 412 5012',
            'is_active' : True,
        }

        response = self.client.put(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_client.refresh_from_db() # read database with updated data
        self.assertEqual(response.data['name'], 'LABORATORIO A ACTUALIZADO')
        self.assertEqual(response.data['nit'], '540.212.322.562.2')

    def test_partial_update_client_patch(self):
        data = {'nit' : '540.210.322.562.2'}

        response = self.client.patch(self.detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_client.refresh_from_db() # read database with updated data
        self.assertEqual(response.data['nit'], '540.210.322.562.2')

    def test_destroy_inactivate_client(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_client.refresh_from_db() # read database with updated data
        self.assertFalse(self.active_client.is_active)