from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import shutil
import tempfile
from .models import User, UserTraceability
from .test_data import UserBaseAdminData, UserBaseProfileData

# temporary folder to store dummy images 
TEST_MEDIA_ROOT = tempfile.mkdtemp()


class UserAdminAPITestCase(UserBaseAdminData, APITestCase):
    """
    test the Admin views endpoints to create, update and "delete" users.
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

        self.url = reverse('user-administration-list')

    def test_create_valid_user(self):
        """
        create a new valid user
        """
        new_user = self.get_valid_user()

        response = self.client.post(self.url, new_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'john_doe')

    def test_create_duplicated_user(self):
        """
        test that 2 users  can't have the same username.
        """
        valid_user = self.get_valid_user() # first create a valid user
        self.client.post(self.url, valid_user, format='json')

        data = self.get_duplicated_user()
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data)

    def test_create_invalid_user(self):
        """
        test that a user can't be created if passwords don't match. 
        """
        data = self.get_invalid_user_password()
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_update_valid_user(self):
        """
        attempting to update a user with justification 
        and check traceability logs for that user.
        """
        new_user = self.get_valid_user() # create the user first
        response = self.client.post(self.url, new_user, format='json')

        # get the id for that new user int the detail url
        new_user_id = response.data['id']
        detail_url = reverse('user-administration-detail', kwargs={'pk': new_user_id})

        updated_user = self.get_update_valid_user()
        response = self.client.patch(detail_url, updated_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['last_name'], 'DOE FIXED')
        
        # check that 2 traceability logs were created
        traceability_logs = UserTraceability.objects.filter(user=new_user_id).order_by('-id')
        self.assertEqual(traceability_logs.count(), 2)

        # check the updated log corresponds
        last_log = traceability_logs[0]
        self.assertEqual(last_log.user_responsible, self.admin_user)
        self.assertIn('APELLIDO', last_log.event)

    def test_update_invalid_user(self):
        """
        attempting to update user with no justification.
        """
        new_user = self.get_valid_user()
        response = self.client.post(self.url, new_user, format='json')

        # get the id for that new user int the detail url
        new_user_id = response.data['id']
        detail_url = reverse('user-administration-detail', kwargs={'pk': new_user_id})

        updated_user = self.get_update_invalid_user()
        response = self.client.patch(detail_url, updated_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)

    def test_destroy_valid_user(self):
        """
        attempting to "destroy" a user with justification 
        and check status change.
        """

        new_user = self.get_valid_user()
        response = self.client.post(self.url, new_user, format='json')

        # get the id for that new user int the detail url
        new_user_id = response.data['id']
        detail_url = reverse('user-administration-detail', kwargs={'pk': new_user_id})

        delete_user = self.get_destroy_valid_user()
        response = self.client.delete(detail_url, delete_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # check status updated to false
        deleted_user = User.objects.get(pk=new_user_id)
        self.assertFalse(deleted_user.is_active)

    def test_destroy_invalid_user(self):
        """
        attempting to "destroy" a user with no justification.
        """
        new_user = self.get_valid_user()
        response = self.client.post(self.url, new_user, format='json')

        # get the id for that new user int the detail url
        new_user_id = response.data['id']
        detail_url = reverse('user-administration-detail', kwargs={'pk': new_user_id})

        delete_user = self.get_destroy_invalid_user()
        response = self.client.delete(detail_url, delete_user, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
    
    def test_retreive_user_traceability(self):
        """
        get a user traceability history.
        """
        new_user = self.get_valid_user() # create user
        response = self.client.post(self.url, new_user, format='json')

        # get the id from the user for the detail url
        user_id = response.data['id']
        detail_url = reverse('user-administration-detail', kwargs={'pk': user_id})

        updated_user = self.get_update_valid_user() # update user

        self.client.patch(detail_url, updated_user, format='json')

        # recover traceability logs
        traceability_url = reverse('user-traceability-user-traceability', kwargs={'user_id': user_id})
        response = self.client.get(traceability_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)


@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT)
class UserSelfUpdateAPITestCase(UserBaseProfileData, APITestCase):
    """
    test the user views endpoints to update their own password or signs.
    """
    def setUp(self):
        self.user = User.objects.create(
            first_name = 'John',
            last_name = 'Doe',
            identification = '987654321',
            email = 'doe@test.com',
            username = 'john_doe',
            job_title = 'Analista de Microbiología',
            rol = 'LABORATORY ANALYST',
        )

        # save hashed password in database
        self.user.set_password('password123')
        self.user.save()

        self.client.force_authenticate(user=self.user)

        self.url_detail = reverse('user-detail', kwargs={'pk': self.user.pk})
    
    @classmethod
    def tearDownClass(cls):
        """
        delete the tempray folder fr sign tests.
        """
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_update_password(self):
        """
        update user password with valid data and check that
        traceability log is created.
        """
        update_data = self.get_update_my_password()

        response = self.client.patch(self.url_detail, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'john_doe')

        # check that 1 traceability log was created (user was created manually creation log will not exist)
        traceability_log = UserTraceability.objects.filter(user=self.user).order_by('-id')
        self.assertEqual(traceability_log.count(), 1)

        # check updating log corresponds
        last_log = traceability_log[0]
        self.assertEqual(last_log.user_responsible, self.user)
        self.assertIn('CONTRASEÑA', last_log.event)

    def test_invalid_password_update(self):
        """
        update password with wrong information or not justification
        """
        # failed update with n justification
        update_data = self.get_update_my_password_no_justification()
        response = self.client.patch(self.url_detail, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response .data)

        # failed updated with passwords missmatch
        update_data = self.get_invalid_update_my_password()
        response = self.client.patch(self.url_detail, update_data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response .data)

    def test_update_signature(self):
        """
        update user signature when need it.
        """
        update_data =  self.get_update_my_signature()

        response = self.client.patch(self.url_detail, update_data)
        
        self.assertEqual(response.status_code,  status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'john_doe')

    def test_forbidden_user(self):
        """
        test that another user tries to update data.
        """
        self.url_detail = reverse('user-detail', kwargs={'pk': 555})

        update_data =  self.get_update_my_password()

        response = self.client.patch(self.url_detail, update_data,  format='json')
        
        self.assertEqual(response.status_code,  status.HTTP_403_FORBIDDEN)
        self.assertIn('error', response.data)
