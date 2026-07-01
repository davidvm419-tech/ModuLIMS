from django.contrib.auth import get_user_model # django will get the custom user model when defined
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import SampleType, Sample, SampleTraceability
from clients.models import Client
from .test_data import SampleTypeBaseData, SampleBaseData


User = get_user_model()


class SampleTypeAPITestCase(SampleTypeBaseData, APITestCase):
    """
    test the sample types views endpoints to create, update and "delete" any type.
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

        self.list_url = reverse('sample-type-list')

    def test_create_valid_type(self):
        """
        Simulates creating a valid type.
        """
        new_sample_type = self.get_valid_type1()
        response = self.client.post(self.list_url, new_sample_type, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'PRODUCTO TERMINADO')

    def test_create_duplicated_type(self):
        """
        create a sample type that already exists in the database.
        """
        new_sample_type = self.get_valid_type1()
        self.client.post(self.list_url, new_sample_type, format='json')

        duplicated_type = self.get_duplicated_type()
        response = self.client.post(self.list_url, duplicated_type, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_invalid_type(self):
        """
        create a new type with missing fields.
        """
        new_sample_type = self.get_invalid_type()
        response = self.client.post(self.list_url, new_sample_type, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_list_active_types(self):
        """
        simulates retreiving a list of sample types, 
        separating active from inactive ones.
        """
        # create 2 valid types and one inactive
        new_sample_type1 = self.get_valid_type1()
        new_sample_type2 = self.get_valid_type2()
        inactive_sample_type = self.get_inactive_type()

        self.client.post(self.list_url, new_sample_type1, format='json')
        self.client.post(self.list_url, new_sample_type2, format='json')
        self.client.post(self.list_url, inactive_sample_type, format='json')

        # get the 2 active types
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['name'], 'AGUA')

    def test_destroy_inactive_type(self):
        """
        attempting to "destroy" a sample type and check status change.
        """
        new_sample_type1 = self.get_valid_type1()
        response = self.client.post(self.list_url, new_sample_type1, format='json')
        
        # get the id from the sample type for the detail url
        sample_type_id = response.data['id']
        detail_url = reverse('sample-type-detail', kwargs={'pk': sample_type_id})
        
        response = self.client.delete(detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        deleted_type = SampleType.objects.get(pk=sample_type_id)
        self.assertFalse(deleted_type.is_active)


class SampleAPITestCase(SampleBaseData, APITestCase):
    """
    test the sample views endpoints to create, update and "delete" samples.
    And retreive sample traceability logs.
    """
    def setUp(self):
        """
        In the set up is include a client and a type to use their ids
        in the tests.
        """
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

        self.client_for_sample = Client.objects.create(
            name = 'LABORATORIO A',
            nit = '540.211.322.562.2',
            address = 'calle real 435 # 11-41',
            contact_person = 'John Doe',
            email = 'alfa@email.com',
            phone = '310 412 5412',
        )

        self.sample_type = SampleType.objects.create(
            name = 'PRODUCTO TERMINADO',
            prefix = 'PT',
        )

        self.list_url = reverse('sample-list')

    def test_create_sample(self):
        """
        create a new valid sample and check that a second sample creation 
        gives the corresponding next code number.
        """
        # create sample and relate ids for client and sample
        new_sample = self.get_valid_sample_1()
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['code'], 'PT2026-1')
        
        # create sample 2
        new_sample2 = self.get_valid_sample_2()
        new_sample2['client'] = self.client_for_sample.id
        new_sample2['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')

        self.assertEqual(response.data['code'], 'PT2026-2')

    def test_create_invalid_sample(self):
        """
        create a new sample with missing fields.
        """
        # create sample and relate ids for client and sample
        new_sample = self.get_create_invalid_sample()
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('description', response.data)

    def test_list_active_samples(self):
        """
        simulates retreiving a list of samples, 
        separating active from inactive ones.
        """
        # create 2 valid samples and one inactive
        new_sample1 = self.get_valid_sample_1()
        new_sample1['client'] = self.client_for_sample.id
        new_sample1['type'] = self.sample_type.id

        new_sample2 = self.get_valid_sample_2()
        new_sample2['client'] = self.client_for_sample.id
        new_sample2['type'] = self.sample_type.id

        inactive_sample = self.get_inactive_sample()
        inactive_sample['client'] = self.client_for_sample.id
        inactive_sample['type'] = self.sample_type.id

        self.client.post(self.list_url, new_sample1, format='json')
        self.client.post(self.list_url, new_sample2, format='json')
        self.client.post(self.list_url, inactive_sample, format='json')

        # get the 2 active samples
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(response.data['results'][0]['code'], 'PT2026-2')

    def test_update_valid_sample(self):
        """
        attempting to update a sample with justification 
        and check traceability logs for that sample.
        """
        new_sample = self.get_valid_sample_1()
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')
        
        # get sample id for detail url
        sample_id = response.data['id']
        detail_url =  reverse('sample-detail', kwargs={'pk': sample_id})
        
        updated_sample = self.get_update_valid_sample()

        response = self.client.patch(detail_url, updated_sample, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['quantity'], '150 TABLETAS')

        # check that 2 traceability logs exist
        traceability_logs = SampleTraceability.objects.filter(sample=sample_id).order_by('-id')
        self.assertEqual(traceability_logs.count(), 2)

        # check that updated log corresponds
        last_log = traceability_logs[0]
        self.assertIn('CANTIDAD', last_log.event)

    def test_update_invalid_sample(self):
        """
        attempting to update a sample with no justification.
        """
        new_sample = self.get_valid_sample_1()
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')
        
        # get sample id for detail url
        sample_id = response.data['id']
        detail_url =  reverse('sample-detail', kwargs={'pk': sample_id})
        
        updated_sample = self.get_update_invalid_sample()

        response = self.client.patch(detail_url, updated_sample, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_destroy_valid_sample(self):
        """
        attempting to "destroy" a sample with justification 
        and check status change.
        """
        new_sample = self.get_valid_sample_1()
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')
        
        # get sample id for detail url
        sample_id = response.data['id']
        detail_url =  reverse('sample-detail', kwargs={'pk': sample_id})
        
        updated_sample = self.get_destroy_valid_sample()

        response = self.client.delete(detail_url, updated_sample, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # check that status was updated
        deleted_sample = Sample.objects.get(pk=sample_id)
        self.assertFalse(deleted_sample.is_active)

    def test_destroy_invalid_sample(self):
        """
        attempting to "destroy" a client with no justification.
        """
        new_sample = self.get_valid_sample_1()
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id

        response = self.client.post(self.list_url, new_sample, format='json')
        
        # get sample id for detail url
        sample_id = response.data['id']
        detail_url =  reverse('sample-detail', kwargs={'pk': sample_id})
        
        updated_sample = self.get_destroy_invalid_sample()

        response = self.client.delete(detail_url, updated_sample, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_retreive_sample_traceability(self):
        """
        get a sample traceability history.
        """
        new_sample = self.get_valid_sample_1() # create sample
        new_sample['client'] = self.client_for_sample.id
        new_sample['type'] = self.sample_type.id
        response = self.client.post(self.list_url, new_sample, format='json')

        # get the sample id for the detail url
        sample_id = response.data['id']
        detail_url = reverse('sample-detail', kwargs={'pk': sample_id})

        updated_sample = self.get_update_valid_sample() # update sample data
        self.client.patch(detail_url, updated_sample, format='json')

        # recover traceability logs
        traceability_url = reverse('sample-traceability-sample-traceability', kwargs={'sample_id': sample_id})
        response = self.client.get(traceability_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
