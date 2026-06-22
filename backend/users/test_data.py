from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase


class UserBaseAdminData(APITestCase):
    """
    base class to create the test data for admin view 
    when creating, updating or inactivating users.
    """
        
    def  get_valid_user(self):
        return {
            'first_name' : 'John',
            'last_name' : 'Doe',
            'identification' : '987654321',
            'email' : 'doe@test.com',
            'username' : 'john_doe',
            'job_title' : 'Analista de Microbiología',
            'rol'  : 'LABORATORY ANALYST',
            'password' : 'password123',
            'password_confirmation' : 'password123',
        }
    
    def get_duplicated_user(self):
        return {
            'first_name' : 'Juan',
            'last_name' : 'Rosal',
            'identification' : '1123456723',
            'email' : 'juan@test.com',
            'username' : 'john_doe',
            'job_title' : 'Analista de Microbiología',
            'rol'  : 'LABORATORY ANALYST',
            'password' : 'password123',
            'password_confirmation' : 'password123',
        }

    def get_invalid_user_password(self):
        return {
            'first_name' : 'John',
            'last_name' : 'Doe',
            'identification' : '987654321',
            'email' : 'doe@test.com',
            'username' : 'john_doe',
            'job_title' : 'Analista de Microbiología',
            'rol'  : 'LABORATORY ANALYST',
            'password' : 'password12',
            'password_confirmation' : 'password123',
        }

    def get_update_valid_user(self):
        return {
            'first_name' : 'John',
            'last_name' : 'Doe fixed',
            'justification' : 'Corrección de apellido.'
        }

    def get_update_invalid_user(self):
        return {
            'first_name' : 'John',
            'last_name' : 'Doe fixed',
        }
    
    def get_destroy_valid_user(self):
        return {
            'justification' : 'Inactivación de usuario pr retiro de la compañía.'
        }

    def get_destroy_invalid_user(self):
        return {}


class UserBaseProfileData(APITestCase):
    """
    base class to create the test data for admin view 
    when creating, updating or inactivating users.
    """
    def get_update_my_password(self):
        return {
            'old_password' : 'password123',
            'new_password' : 'newsecurepassword123', 
            'new_password_confirmation' : 'newsecurepassword123',
            'justification' : 'Actualización de contraseña.',
        }
    
    def get_update_my_password_no_justification(self):
        return {
            'old_password' : 'password123',
            'new_password' : 'newsecurepassword123', 
            'new_password_confirmation' : 'newsecurepassword123',
        }

    def get__invalid_update_my_password(self):
        return {
            'old_password' : 'password123',
            'new_password' : 'newsecurepassword123', 
            'new_password_confirmation' : 'newsecurepassword',
            'justification' : 'Actualización de contraseña.',
        }
    
    def get_update_my_signature(self):
        # simulated image
        signature_png = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c\x04\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00\x02\x00\x01H\xaf\xa4q\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        
        simulated_image = SimpleUploadedFile(
            name = 'Firma_John.png',
            content = signature_png,
            content_type='image/png', 
        )
        
        return {
            'sign' : simulated_image,
            'justification' : 'Actualización de firma.',
        } 
