from rest_framework.test import APITestCase


class ClientBaseData(APITestCase):
    """
    base class to create the test data for views 
    when creating, updating or inactivating clients.
    """
        
    def  get_valid_client_1(self):
        return {
            'name' : 'LABORATORIO A',
            'nit' : '540.211.322.562.2',
            'address' : 'calle real 435 # 11-41',
            'contact_person' : 'John Doe',
            'email' : 'alfa@email.com',
            'phone' : '310 412 5412',
        }
    
    def get_valid_client_2(self):
        return {
            'name' : 'LABORATORIO F',
            'nit' : '120.511.411.132.1',
            'address' : 'calle 123 # 37-11',
            'contact_person' : 'God Doe',
            'email' : 'god@email.com',
            'phone' : '300 342 1121',
        }
    
    def get_inactive_client(self):
        return {
            'name' : 'LABORATORIO Z',
            'nit' : '145.111.442.321.2',
            'address' : 'calle falsa 123 # 37-11',
            'contact_person' : 'False Doe',
            'email' : 'falso@email.com',
            'phone' : '301 312 3151',
            'is_active': False
        }
    
    def get_duplicated_client(self):
        return {
            'name' : 'LABORATORIO A',
            'nit' : '540.211.322.562.1',
            'address' : 'calle real 435 # 11-41',
            'contact_person' : 'John Doe',
            'email' : 'alfa@email.com',
            'phone' : '310 412 5412',
        }

    def get_invalid_client(self):
        return {
            'name' : 'laboratorio a',
            'nit' : '',
            'address' : '',
            'contact_person' : '',
            'email' : 'm@email.com',
            'phone' : '312 412 4321',
        }

    def get_update_valid_client(self):
        return {
            'name' : 'LABORATORIO A FIXED',
            'phone' : '310 412 5311',
            'justification' : 'Corrección de nombre.'
        }

    def get_update_invalid_client(self):
        return {
            'name' : 'LABORATORIO AB',
            'phone' : '310 412 5311',
        }
    
    def get_destroy_valid_client(self):
        return {
            'justification' : 'Inactivación de cliente por actualización de razón social.'
        }

    def get_destroy_invalid_client(self):
        return {}
