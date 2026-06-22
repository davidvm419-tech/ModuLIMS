from rest_framework import serializers
from .models import SampleType, Sample, SampleTraceability


class SampleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleType
        fields = '__all__'

    def to_internal_value(self, data):
        '''
        cleans the data to avoid multiple names of the same sample type and white spaces.
        '''
        clean_data = data.copy()

        for key, value in clean_data.items():
            if isinstance(value, str):
                clean_data[key] = value.strip().upper()

        return super().to_internal_value(clean_data)


class SampleTraceabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleTraceability
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sample
        fields = '__all__'
        # DRF will allow this data to not be send into the backend, so the logic can be added in that moment
        read_only_fields = ['code', 'received_date']

    def to_internal_value(self, data):
        '''
        cleans the data to avoid white spaces on the data.
        '''
        clean_data = data.copy()

        for key, value in clean_data.items():
            if isinstance(value, str):
                clean_data[key] = value.strip().upper() 
                
        return super().to_internal_value(clean_data)  
