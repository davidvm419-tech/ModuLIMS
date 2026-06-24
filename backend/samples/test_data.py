from rest_framework.test import APITestCase


class SampleTypeBaseData(APITestCase):
    """
    base class to create the test data for views 
    when creating, updating or inactivating samples types.
    """
    def  get_valid_type1(self):
        return {
            'name' : 'Producto terminado',
            'prefix' : 'PT',
        }
    
    def  get_valid_type2(self):
        return {
            'name' : 'AGUA',
            'prefix' : 'AG',
        }
    
    def  get_inactive_type(self):
        return {
            'name' : 'MATERIA PRIMA',
            'prefix' : 'MP',
            'is_active' : False,
        }
    
    def  get_duplicated_type(self):
        return {
            'name' : 'Producto terminado',
            'prefix' : 'PT',
        }
    
    def  get_invalid_type(self):
        return {
            'name' : '',
            'prefix' : 'ME',
        }
    

class SampleBaseData(APITestCase):
    """
    base class to create the test data for views 
    when creating, updating or inactivating samples.
    """
    def  get_valid_sample_1(self):
        return {
            'client' : 1,
            'name' : 'TABLETA DE ACETAMINOFÉN',
            'type' : 1,
            'manufacturing_date' : '2026-01-03',
            'expiration_date' : '2028-01-03',
            'description' : 'tableta blanca valada sin partículas extrañas',
            'quantity' : '100 tabletas',
            'observations' : 'na',
        }
    
    def  get_valid_sample_2(self):
        return {
            'client' : 1,
            'name' : 'Agua purificada (punto 1)',
            'type' : 1,
            'manufacturing_date' : '2026-03-05',
            'expiration_date' : '2026-03-06',
            'description' : 'liquido transparente sin partículas extrañas',
            'quantity' : '500 ml',
            'observations' : 'mantener en refrigeración y reprtar como producto terminado',
        }
        
    def  get_inactive_sample(self):
        return {
            'client' : 1,
            'name' : 'Cafeína',
            'type' : 1,
            'manufacturing_date' : '2026-06-01',
            'expiration_date' : '2029-06-01',
            'description' : 'polvo blanco sin partículas extrañas',
            'quantity' : '100 gramos',
            'observations' : 'na',
            'is_active': False,
        }
    
    def  get_create_invalid_sample(self):
        return {
            'client' : 1,
            'name' : 'Cafeína',
            'type' : 1,
            'manufacturing_date' : '2026-06-01',
            'expiration_date' : '2029-06-01',
            'description' : '',
            'quantity' : '100 gramos',
            'observations' : '',
        }
    
    def get_update_valid_sample(self):
        return {
            'quantity' : '150 tabletas',
            'justification' : 'Corrección en cantidad de muestra enviada.'
        }

    def get_update_invalid_sample(self):
        return {
            'quantity' : '150 tabletas',
        }
    
    def get_destroy_valid_sample(self):
        return {
            'justification' : 'Inactivación de muestra ya que el cliente cancela el análisis.'
        }

    def get_destroy_invalid_sample(self):
        return {}