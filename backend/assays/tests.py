from django.contrib.auth import get_user_model # django will get the custom user model when defined
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Assay,  AssayTraceability, SampleAssay
from clients.models import Client
from samples.models import SampleType, Sample, SampleTraceability
from .test_data import AssayBaseData, SampleAssayBaseData


User = get_user_model()


class AssayAPITestCase(AssayBaseData, APITestCase):
    """
    test the assay views endpoints to create, update and "delete" any assay.
    And retreive sample traceability logs.
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

        self.list_url = reverse('assay-list')

    def test_create_valid_assay(self):
        """
        Simulates creating a valid assay.
        """
        new_assay = self.get_valid_assay1()
        response = self.client.post(self.list_url, new_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['methodology'], 'POS-M-001')

    def test_create_duplicated_assay(self):
        """
        create an assay that already has that methodology in the database.
        """
        # create a new assay
        new_assay = self.get_valid_assay2()
        self.client.post(self.list_url, new_assay, format='json')
        
        duplicated_assay = self.get_duplicated_assay()
        response = self.client.post(self.list_url, duplicated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('methodology', response.data)

    def  test_create_invalid_assay(self):
        """
        create a new assay with missing fields.
        """
        invalid_assay = self.get_create_invalid_assay()

        response = self.client.post(self.list_url, invalid_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('normative_reference', response.data)

    def test_list_active_assays(self):
        """
        simulates retreiving a list of assays, 
        separating active from inactive ones.
        """
        # create 2 valid assays and one inactive
        new_assay1 = self.get_valid_assay1()
        new_assay2 = self.get_valid_assay2()
        inactive_assay = self.get_inactive_assay()

        self.client.post(self.list_url, new_assay1, format='json')
        self.client.post(self.list_url, new_assay2, format='json')
        self.client.post(self.list_url, inactive_assay, format='json')

        # get the 2 active assays
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['methodology'], 'POS-M-002')
    
    def test_update_valid_assay(self):
        """
        attempting to update an assay with justification 
        and check traceability logs for that assay.
        """
        new_assay = self.get_valid_assay1()
        response = self.client.post(self.list_url, new_assay, format='json')

        # get assay id for detail url
        assay_id = response.data['id']
        detail_url = reverse('assay-detail', kwargs={'pk' : assay_id})

        updated_assay = self.get_update_valid_assay()

        response = self.client.patch(detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['methodology'], 'POS-M-012')

        # check that 2 traceability logs exist
        traceability_logs = AssayTraceability.objects.filter(assay=assay_id).order_by('-id')
        self.assertEqual(traceability_logs.count(), 2)

        # check that updated log corresponds
        last_log = traceability_logs[0]
        self.assertIn('ACTUALIZACIÓN', last_log.event)

    def test_update_invalid_assay(self):
        """
        attempting to update an assay with no justification.
        """
        new_assay = self.get_valid_assay1()
        response = self.client.post(self.list_url, new_assay, format='json')

        # get assay id for detail url
        assay_id = response.data['id']
        detail_url = reverse('assay-detail', kwargs={'pk' : assay_id})

        updated_assay = self.get_update_invalid_assay()

        response = self.client.patch(detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_destroy_valid_sample(self):
        """
        attempting to "destroy" aan assay with justification 
        and check status change.
        """
        new_assay = self.get_valid_assay1()
        response = self.client.post(self.list_url, new_assay, format='json')

        # get assay id for detail url
        assay_id = response.data['id']
        detail_url = reverse('assay-detail', kwargs={'pk' : assay_id})

        updated_assay = self.get_destroy_valid_assay()

        response = self.client.delete(detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # check that status was updated
        deleted_assay = Assay.objects.get(pk=assay_id)
        self.assertFalse(deleted_assay.is_active)

    def test_destroy_invalid_assay(self):
        """
        attempting to "destroy" an assay with no justification.
        """
        new_assay = self.get_valid_assay1()
        response = self.client.post(self.list_url, new_assay, format='json')

        # get assay id for detail url
        assay_id = response.data['id']
        detail_url = reverse('assay-detail', kwargs={'pk' : assay_id})

        updated_assay = self.get_destroy_invalid_assay()

        response = self.client.delete(detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_retreive_sample_traceability(self):
        """
        get an assay traceability history.
        """
        new_assay = self.get_valid_assay1()
        response = self.client.post(self.list_url, new_assay, format='json')

        # get assay id for detail url
        assay_id = response.data['id']
        detail_url = reverse('assay-detail', kwargs={'pk' : assay_id})

        updated_assay = self.get_update_valid_assay() # update assay

        response = self.client.patch(detail_url, updated_assay, format='json')

        # recover traceability logs
        traceability_url = reverse('assay-traceability-assay-traceability', kwargs={'assay_id' : assay_id})
        response = self.client.get(traceability_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)


class SampleAssayAPITestCase(SampleAssayBaseData, APITestCase):
    """
    test the sample assay views endpoints to update and delete any sample assay.
    And retreive sample traceability logs.
    """
    def setUp(self):
        """
        In the set up is include a client, sample, sample type and  assay to use their ids
        in the tests for t he database relationships.
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

        self.sample = Sample.objects.create(
            client = self.client_for_sample,
            name = 'TABLETA DE ACETAMINOFÉN',
            type = self.sample_type,
            manufacturing_date = '2026-01-03',
            expiration_date = '2028-01-03',
            description = 'TABLETA BLANCA OVALADA SIN PARTÍCULAS EXTRAÑAS',
            quantity = '100 TABLETAS',
            observations = 'NA',
        )

        self.assay1 = Assay.objects.create(
            name = 'RECUENTO DE MICROORGANISMOS MESOFILOS AEROBIOS',
            category = 'MICROBIOLOGY',
            methodology = 'POS-M-001',
            normative_reference = 'USP NF 61',
        )

        self.assay2 = Assay.objects.create(
            name = 'RECUENTO DE HONGOS Y LEVADURAS',
            category = 'MICROBIOLOGY',
            methodology = 'POS-M-002',
            normative_reference = 'USP NF 61',
        )

        self.sample_assay1 = SampleAssay.objects.create(
            sample = self.sample,
            assay = self.assay1,
            specification = '<=1000',
            units = 'UFC/mL',
        )

        self.sample_assay2 = SampleAssay.objects.create(
            sample = self.sample,
            assay = self.assay2,
            specification = '<=100',
            units = 'UFC/mL',
        )
        
        self.list_url = reverse('sample-assay-list')
        self.detail_url =  reverse('sample-assay-detail', kwargs={'pk': self.sample_assay1.pk})
    
    def test_list_sample_assays(self):
        """
        test that the list method returns the assays for a particular sample.
        """
        response = self.client.get(self.list_url, data={'sample_id': self.sample.pk}) # send the sample id in  the request
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_sample_assays_no_sample_id(self):
        """
        attempting to get assays with no sample id
        """
        response = self.client.get(self.list_url) # send the sample id in  the request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_valid_sample_assay(self):
        """
        attempting to update a sample assay with justification 
        and check traceability logs for that sample.
        """
        updated_assay = self.get_update_valid_sample_assay()

        response = self.client.patch(self.detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['specification'], '<=500')

        # check that 1 traceability logs exist 
        # (because the sample was created manually not traceability log was created)
        traceability_logs = SampleTraceability.objects.filter(sample=self.sample.id).order_by('-id')
        self.assertEqual(traceability_logs.count(), 1)

        log = traceability_logs[0]

        # check that updated log corresponds
        self.assertIn('ERROR', log.event)
    
    def test_update_invalid_sample_assay(self):
        """
        attempting to update a sample assay with no justification 
        """
        updated_assay = self.get_update_invalid_sample_assay()

        response = self.client.patch(self.detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_destroy_valid_assay(self):
        """
        attempting to delete an  assay with justification 
        and check that was delete it and check that traceability log was created.
        """
        updated_assay = self.get_destroy_valid_sample_assay()

        response = self.client.delete(self.detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

        # check that 1 traceability logs exist 
        # (because the sample was created manually not traceability log was created)
        traceability_logs = SampleTraceability.objects.filter(sample=self.sample.id).order_by('-id')
        log = traceability_logs[0]
        self.assertIn('ELIMINA', log.event)

        # check sample has 1 assay
        response = self.client.get(self.list_url, data={'sample_id': self.sample.pk})
        self.assertEqual(len(response.data), 1)
        print(response.data)

    def test_destroy_invalid_assay(self):
        """
        attempting to delete an assay with no justification.
        """
        updated_assay = self.get_destroy_invalid_sample_assay()

        response = self.client.delete(self.detail_url, updated_assay, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
