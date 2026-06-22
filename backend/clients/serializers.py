from rest_framework import serializers
from .models import Client, ClientTraceability 


class ClientSerializer(serializers.ModelSerializer):
    class  Meta:
        model = Client
        fields = '__all__'
    
    def to_internal_value(self, data):
        '''
        cleans the data to avoid multiple names of the same client and white spaces.
        '''
        clean_data = data.copy()

        for key, value in clean_data.items():
            if isinstance(value, str):
                clean_data[key] = value.strip()

                if key == 'name':
                    clean_data[key] = value.strip().upper()

        return super().to_internal_value(clean_data)
    

class ClientTraceabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientTraceability
        fields = '__all__'  