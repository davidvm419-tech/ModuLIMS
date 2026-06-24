from django.contrib.auth import get_user_model # django will get the custom user model when defined
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Client, ClientTraceability
from .test_data import ClientBaseData


User = get_user_model()


class ClientAPITestCase(ClientBaseData, APITestCase):
    """
    test the client views endpoints to create, update and "delete" clients.
    And retreive client traceability logs.
    """
    def setUp(self):
        self.admin_user = User.objects.create(
            first_name = 'Peter',
            last_name = 'Admin',
            identification = '12954321789',
            email = 'peter@test.com',
            username = 'peter_admin',
            job_title = 'Coordinador de Labratorio',
            rol = 'LABORATORY COORDINATOR',
        )

        # save hashed password in database
        self.admin_user.set_password('superpassword123')
        self.admin_user.save()

        self.client.force_authenticate(user=self.admin_user)

        self.list_url = reverse('client-list')

    def test_create_valid_client(self):
        """
        create a new valid client.
        """
        new_client = self.get_valid_client_1()
        response = self.client.post(self.list_url, new_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['nit'], '540.211.322.562.2')

    def test_create_duplicated_client(self):
        """
        create a client that already exists in the database.
        """
        new_client = self.get_valid_client_1() # valid client creation
        self.client.post(self.list_url, new_client, format='json')

        duplicated_client = self.get_duplicated_client()
        response = self.client.post(self.list_url, duplicated_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_invalid_client(self):
        """
        create a new client with missing fields.
        """
        new_client = self.get_invalid_client()
        
        response = self.client.post(self.list_url, new_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nit', response.data)
        self.assertIn('address', response.data)

    def test_list_active_clients(self):
        """
        simulates retreiving a list of clients, 
        separating active from inactive ones.
        """
        # create 2 valid clients and one inactive
        first_client = self.get_valid_client_1()
        second_client = self.get_valid_client_2()
        inactive_client = self.get_inactive_client()

        self.client.post(self.list_url, first_client, format='json')
        self.client.post(self.list_url, second_client, format='json')
        self.client.post(self.list_url, inactive_client, format='json')

        # get the 2 active clients
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'LABORATORIO A')    

    def test_update_valid_client(self):
        """
        attempting to update a client with justification 
        and check traceability logs for that user.
        """
        new_client = self.get_valid_client_1()
        response = self.client.post(self.list_url, new_client, format='json')

        # get the id from the client for the detail url
        client_id = response.data['id']
        detail_url = reverse('client-detail', kwargs={'pk': client_id})

        updated_client = self.get_update_valid_client()

        response = self.client.patch(detail_url, updated_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], '310 412 5311')

        # check that 2 traceability logs exist 
        traceability_logs = ClientTraceability.objects.filter(client=client_id).order_by('-id')
        self.assertEqual(traceability_logs.count(), 2)

        # check the updated log corresponds
        last_log = traceability_logs[0]
        self.assertIn('CORRECCIÓN', last_log.event)

    def test_update_invalid_client(self):
        """
        attempting to update a client with no justification.
        """
        new_client = self.get_valid_client_1()
        response = self.client.post(self.list_url, new_client, format='json')

        # get the id from the client for the detail url
        client_id = response.data['id']
        detail_url = reverse('client-detail', kwargs={'pk': client_id})

        updated_client = self.get_update_invalid_client()

        response = self.client.patch(detail_url, updated_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_destroy_valid_client(self):
        """
        attempting to "destroy" a client with justification 
        and check status change.
        """
        new_client = self.get_valid_client_1()
        response = self.client.post(self.list_url, new_client, format='json')

        # get the id from the client for the detail url
        client_id = response.data['id']
        detail_url = reverse('client-detail', kwargs={'pk': client_id})

        delete_client = self.get_destroy_valid_client()

        response = self.client.delete(detail_url, delete_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # check status updated to false
        deleted_client = Client.objects.get(pk=client_id)
        self.assertFalse(deleted_client.is_active)
    
    def test_destroy_invalid_client(self):
        """
        attempting to "destroy" a client with no justification.
        """
        new_client = self.get_valid_client_1()
        response = self.client.post(self.list_url, new_client, format='json')

        # get the id from the client for the detail url
        client_id = response.data['id']
        detail_url = reverse('client-detail', kwargs={'pk': client_id})

        delete_client = self.get_destroy_invalid_client()

        response = self.client.delete(detail_url, delete_client, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_retreive_client_traceability(self):
        """
        get a client traceability history.
        """
        new_client = self.get_valid_client_1() # create client
        response = self.client.post(self.list_url, new_client, format='json')

        # get the id from the client for the detail url
        client_id = response.data['id']
        detail_url = reverse('client-detail', kwargs={'pk': client_id})

        updated_client = self.get_update_valid_client() # update client
        self.client.patch(detail_url, updated_client, format='json')

        # recover traceability logs
        traceability_url = reverse('client-traceability-client-traceability', kwargs={'client_id': client_id})
        response = self.client.get(traceability_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
