from  datetime import timedelta
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework.test import APITestCase
import shutil
import tempfile
from .models import User, UserTraceability
from .test_data import UserBaseAdminData, UserBaseProfileData

# temporary folder to store dummy images 
TEST_MEDIA_ROOT = tempfile.mkdtemp()


class UserAdminAPITestCase(UserBaseAdminData, APITestCase):
    """
    test the Admin views endpoints to create, update, "delete" users.
    And Retreive user traceability logs.
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
    test the user views endpoints to login, update their own password or signs.
    Also test that the JWT validity.
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

        self.login_url = reverse('user-login')
        self.url_detail = reverse('user-detail', kwargs={'pk': self.user.pk})
    
    @classmethod
    def tearDownClass(cls):
        """
        delete the temporay folder for sign tests.
        """
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def test_valid_user_login(self):
        """
        login a valid user and check that  return data corresponds.
        """
        self.client.force_authenticate(user=None) # close set up session

        data = {
            'username': self.user.username,
            'password': 'password123',
        }

        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], self.user.username)
    
    def test_inactive_user_login(self):
        """
        attempt to login with an inactive user.
        """
        self.client.force_authenticate(user=None) # close set up session

        self.user.is_active = False # change user status
        self.user.save()

        data = {
            'username': self.user.username,
            'password': 'password123',
        }

        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('usuario inactivo', response.data['error'])

    def test_invalid_user_login(self):
        """
        attempt to login with wrong credentials 
        or empty credentials.
        """
        self.client.force_authenticate(user=None) # close set up session

        # wrong credentials
        data = {
            'username': self.user.username,
            'password': 'password',
        }

        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('acceso incorrectas', response.data['error'])

        #  empty data
        data['password'] = ''

        response = self.client.post(self.login_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('acceso incompletas', response.data['error'])

    def test_access_token(self):
        """
        login a valid user and check that the access JWT is valid on the defined times.
        """
        self.client.force_authenticate(user=None) # close set up session

        access_token = AccessToken.for_user(self.user) # create a token for the user

        access_token.set_exp(lifetime=timedelta(minutes=7)) # set a valid lifetime for this token

        valid_access_token = str(access_token)

        self.client.credentials(HTTP_AUTHORIZATION=F"Bearer {valid_access_token}") # add the token to user credentials
        
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
    
    def test_invalid_access_token(self):
        """
        login a valid user and check that the access JWT is invalid on the defined times.
        """
        self.client.force_authenticate(user=None) # close set up session
        
        access_token = AccessToken.for_user(self.user) # create a token for the user

        access_token.set_exp(lifetime=-timedelta(minutes=5)) # set the token as invalid

        invalid_access_token = str(access_token) 

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {invalid_access_token}") # add the token to user credentials
        response = self.client.get(self.url_detail)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('token_not_valid', response.data['code'])
        
    def test_refresh_token(self):
        """
        login a valid user and check that the refresh JWT is valid on the defined times.
        """
        self.client.force_authenticate(user=None) # close set up session

        refresh_token = RefreshToken.for_user(self.user) # create a token for the user

        refresh_token.set_exp(lifetime=timedelta(minutes=25)) # set a valid lifetime for this token

        valid_refresh_token = str(refresh_token)

        refresh_url = reverse('token_refresh') # url for the refresh token

        data = {'refresh': valid_refresh_token} # send the token on request body

        response = self.client.post(refresh_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # ensuring both tokens are returned for the token rotation configuration
        self.assertIn('refresh', response.data)
        self.assertIn('access', response.data)
    
    def test_invalid_refresh_token(self):
        """
        login a valid user and check that the refresh JWT is invalid on the defined times.
        """
        self.client.force_authenticate(user=None) # close set up session

        refresh_token = RefreshToken.for_user(self.user) # create a token for the user

        refresh_token.set_exp(lifetime=-timedelta(minutes=32)) # set a invalid lifetime for this token

        valid_refresh_token = str(refresh_token)

        refresh_url = reverse('token_refresh') # url for the refresh token

        data = {'refresh': valid_refresh_token} # send the token on request body

        response = self.client.post(refresh_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('token_not_valid', response.data['code'])

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
