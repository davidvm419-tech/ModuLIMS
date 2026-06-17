from django.contrib.auth import get_user_model # django will get the custom user model when defined
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Client, SampleType, Sample, SampleTraceability

User = get_user_model()

# Create your tests here.
class ClientAPITestCase(APITestCase):
    def setUp(self):
        """
        test data for client views
        """
        self.user = User.objects.create_user(
            username = 'analista1',
            password = 'password123'
        )

        self.client.force_authenticate(user=self.user)

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
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_201_CREATED)
        self.assertTrue(Client.objects.filter(nit='121.430.223.111').exists())      

    def test_create_duplicated_client(self):
        data = {
            'name' : 'laboratorio a',
            'nit' : '123.433.223.111',
            'address' : 'calle 51 # 2-1',
            'contact_person' : 'Many Ice',
            'email' : 'm@email.com',
            'phone' : '312 412 4321',
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_client_missing_fields(self):
        data = {
            'name' : 'laboratorio a',
            'nit' : '',
            'address' : '',
            'contact_person' : '',
            'email' : 'm@email.com',
            'phone' : '312 412 4321',

        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code,  status.HTTP_400_BAD_REQUEST)
        self.assertIn('nit', response.data)
        self.assertIn('address', response.data)
        self.assertIn('contact_person', response.data)

    def test_destroy_inactivate_client(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_client.refresh_from_db() # read database with updated data
        self.assertFalse(self.active_client.is_active)


class SampleTypeAPITestCase(APITestCase):
    def setUp(self):
        """
        test data for sample types
        """
        self.user = User.objects.create_user(
            username = 'analista1',
            password = 'password123'
        )

        self.client.force_authenticate(user=self.user)

        self.active_type = SampleType.objects.create(
            name = 'PRODUCTO TERMINADO',
            prefix = 'PT',
            is_active = True
        )

        self.disabled_type = SampleType.objects.create(
            name = 'MATERIA PRIMA',
            prefix = 'M',
            is_active = False
        )

        self.list_url = reverse('sample-type-list')
        self.detail_url = reverse('sample-type-detail', kwargs={'pk': self.active_type.pk})

    def test_list_active_types(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'PRODUCTO TERMINADO')

    def test_create_valid_type(self):
        data = {
            'name' : 'Agua',
            'prefix' : 'AG',
            'is_active' : True,
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(SampleType.objects.filter(name='AGUA').exists())

    def test_create_duplicated_type(self):
        data = {
            'name' : 'Producto terminado',
            'prefix' : 'P',
            'is_active' : True,
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)

    def test_create_type_missing_fields(self):
        data = {
            'name' : '',
            'prefix' : 'AT',
            'is_active' : True,
        }

        response = self.client.post(self.list_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
  

    def test_destroy_inactive_type(self):
        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_type.refresh_from_db() # read database with updated data
        self.assertFalse(self.active_type.is_active)


class SampleAPITestCase(APITestCase):
    def setUp(self):
        """
        test data for samples
        """
        self.user = User.objects.create_user(
            username = 'analista1',
            password = 'password123'
        )

        self.client.force_authenticate(user=self.user)

        self.sample_client  = Client.objects.create(
            name = 'LABORATORIO A',
            nit = '540.211.322.562.2',
            address = 'calle real 435 # 11-41',
            contact_person = 'John Doe',
            email = 'alfa@email.com',
            phone = '310 412 5412',
            is_active = True,
        )

        self.type = SampleType.objects.create(
            name = 'PRODUCTO TERMINADO',
            prefix = 'PT',
            is_active = True
        )

        self.active_sample = Sample.objects.create(
            client = self.sample_client,
            code = 'PT2026-1',
            name = 'TABLETA DE ACETAMINOFÉN',
            type = self.type,
            manufacturing_date = '2026-01-03',
            expiration_date = '2028-01-03',
            description = 'TABLETA BLANCA OVALADA SIN PARTÍCULAS EXTRAÑAS',
            quantity = '100 TABLETAS',
            observations = 'NA',
            received_date = '2026-04-01',
            status = 'RECEIVED',
            is_active = True,
        )

        self.inactive_sample = Sample.objects.create(
            client = self.sample_client,
            code = 'M2026-1',
            name = 'POLVO DE ACETAMINOFÉN',
            type = self.type,
            manufacturing_date = '2025-02-03',
            expiration_date = '2029-02-03',
            description = 'POLVO BLANCO SIN PARTÍCULAS EXTRAÑAS',
            quantity = '100 GRAMOS',
            observations = 'NA',
            received_date = '2026-02-01',
            status = 'RECEIVED',
            is_active = False,
        )

        self.list_url = reverse('sample-list')
        self.detail_url = reverse('sample-detail', kwargs={'pk': self.active_sample.pk})

    def test_list_active_samples(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['code'], 'PT2026-1')

    def test_create_sample(self):
        """
        for sample creation also assert that traceability log is store in the database.
        """
        data = {
            'client' : self.sample_client.id,
            'name' : 'Cápsulas de omega 3',
            'type' : self.type.id,
            'manufacturing_date' : '2026-01-01',
            'expiration_date' : '2029-01-01',
            'description' : 'CÁPSULA color cafe ovalada SIN PARTÍCULAS EXTRAÑAS',
            'quantity' : '100 gramos',
            'observations' : 'na',
        }

        response = self.client.post(self.list_url, data, format='json')
        
        self.assertEqual(response.status_code,  status.HTTP_201_CREATED)
        self.assertEqual(response.data['observations'],  'NA')
        self.assertEqual(response.data['code'], 'PT2026-2')    
       
        # get sample
        sample = Sample.objects.get(code='PT2026-2')
        
        # check that traceability was created
        traceability_exist = SampleTraceability.objects.filter(sample=sample).exists()  

        # Check if traceability was created or not 
        self.assertTrue(traceability_exist, 'Error, traceability was not created!')

        # check traceability log
        traceability_log = SampleTraceability.objects.filter(sample=sample).order_by('-id').first()
        self.assertEqual(traceability_log.user_responsible, self.user)
        self.assertEqual(traceability_log.event, 'MUESTRA INGRESADA EN EL SISTEMA')  

    def test_retrieve_sample(self):
        response = self.client.get(self.detail_url)
        self.assertEqual(response.data['code'], 'PT2026-1')
        self.assertEqual(response.data['name'], 'TABLETA DE ACETAMINOFÉN')

    def test_invalid_update_sample_put(self):
        """
        assert that justification log is not sended.
        """

        data = {
            'client' : self.sample_client.id,
            'name' : 'TABLETA DE ACETAMINOFÉN 500 mg',
            'type' : self.type.id,
            'manufacturing_date' : '2026-02-01',
            'expiration_date' : '2029-02-01',
            'description' : 'TABLETA blanca OVALADA SIN PARTÍCULAS EXTRAÑAS',
            'quantity' : '150 gramos',
            'observations' : 'Incluir en el certificado muestra de estabilidad',
        }

        response = self.client.put(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)  

    def test_invalid_update_sample_patch(self):
        """
        assert that justification log is not sended.
        """

        data = {
            'observations' : 'Incluir en el certificado muestra de estabilidad',
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)      

    def test_update_sample_put(self):
        """
        assert that traceability log is store in the database.
        """

        data = {
            'client' : self.sample_client.id,
            'name' : 'TABLETA DE ACETAMINOFÉN 500 mg',
            'type' : self.type.id,
            'manufacturing_date' : '2026-02-01',
            'expiration_date' : '2029-02-01',
            'description' : 'TABLETA blanca OVALADA SIN PARTÍCULAS EXTRAÑAS',
            'quantity' : '150 gramos',
            'observations' : 'Incluir en el certificado muestra de estabilidad',
            'justification': 'Error por parte del cliente en la información de la muestra enviada'
        }

        response = self.client.put(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_sample.refresh_from_db() # read database with updated data
        self.assertEqual(response.data['name'], 'TABLETA DE ACETAMINOFÉN 500 MG')
        self.assertEqual(response.data['quantity'], '150 GRAMOS')

        # get sample
        sample = Sample.objects.get(code='PT2026-1')

        # check traceability log
        traceability_log = SampleTraceability.objects.filter(sample=sample).order_by('-id').first()
        self.assertEqual(traceability_log.user_responsible, self.user)
        self.assertIn('CLIENTE', traceability_log.event)

    def test_update_sample_patch(self):
        """
        assert that traceability log is store in the database.
        """
                
        data = {
            'observations' : 'Incluir en el certificado muestra de estabilidad',
            'justification': 'Cliente solicita incluir observación'
        }

        response = self.client.patch(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_sample.refresh_from_db() # read database with updated data
        self.assertEqual(response.data['observations'], 'INCLUIR EN EL CERTIFICADO MUESTRA DE ESTABILIDAD')

        # get sample
        sample = Sample.objects.get(code='PT2026-1')

        # check traceability log
        traceability_log = SampleTraceability.objects.filter(sample=sample).order_by('-id').first()
        self.assertEqual(traceability_log.user_responsible, self.user)
        self.assertIn('OBSERVACIÓN', traceability_log.event)

    def test_invalid_destroy_inactivate_sample(self):
        """
        assert that justification is not sended with the data.
        """

        response = self.client.delete(self.detail_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_destroy_inactivate_sample(self):
        """
        assert that traceability log is store in the database.
        """
        data = {
            'justification': 'Cliente cancela el ensayo de la muestra.'
        }

        response = self.client.delete(self.detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.active_sample.refresh_from_db() # read database with updated data
        self.assertFalse(self.active_sample.is_active)

        # get sample
        sample =Sample.objects.get(code='PT2026-1')

        # check that traceability
        traceability_log = SampleTraceability.objects.filter(sample=sample).order_by('-id').first()
        self.assertEqual(traceability_log.user_responsible, self.user)
        self.assertIn('CANCELA', traceability_log.event)


class SampleTraceabilityAPITestCase(APITestCase):
    def setUp(self):
        """
        test data for sample traceability
        """
        self.user = User.objects.create_user(
            username = 'analista1',
            password = 'password123'
        )

        self.client.force_authenticate(user=self.user)

        self.sample_client  = Client.objects.create(
            name = 'LABORATORIO A',
            nit = '540.211.322.562.2',
            address = 'calle real 435 # 11-41',
            contact_person = 'John Doe',
            email = 'alfa@email.com',
            phone = '310 412 5412',
            is_active = True,
        )

        self.type = SampleType.objects.create(
            name = 'PRODUCTO TERMINADO',
            prefix = 'PT',
            is_active = True
        )

        self.sample = Sample.objects.create(
            client = self.sample_client,
            code = 'PT2026-1',
            name = 'TABLETA DE ACETAMINOFÉN',
            type = self.type,
            manufacturing_date = '2026-01-03',
            expiration_date = '2028-01-03',
            description = 'TABLETA BLANCA OVALADA SIN PARTÍCULAS EXTRAÑAS',
            quantity = '100 TABLETAS',
            observations = 'NA',
            received_date = '2026-04-01',
            status = 'RECEIVED',
            is_active = True,
        )
          
        self.sample_traceability1 = SampleTraceability.objects.create(
            sample = self.sample,
            user_responsible = self.user,
            event = 'MUESTRA INGRESADA EN EL SISTEMA',
            event_date = '2026-01-03',
        )

        self.sample_traceability2 = SampleTraceability.objects.create(
            sample = self.sample,
            user_responsible = self.user,
            event = 'INCLUIR EN EL CERTIFICADO MUESTRA DE ESTABILIDAD',
            event_date = '2026-01-05',
        )

        self.list_url = reverse('traceability-sample-traceability', kwargs={'sample_id': self.sample.pk})

    def test_retreive_sample_traceability(self):
        
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)