from rest_framework import serializers
from .models import Client, SampleCategory, Sample, SampleTraceability


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
            



class SampleCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleCategory
        fields = '__all__'


class SampleTraceabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SampleTraceability
        fields = '__all__'


class SampleSerializer(serializers.ModelSerializer):
    # Get the traceability data into the serializer for that sample
    traceability_logs = SampleTraceabilitySerializer(many=True, read_only=True)    
    class Meta:
        model = Sample
        fields = '__all__'
        # DRF will allow this data to nt be send into the backend, soo the logic can be added in that moment
        read_only_fields = ['code', 'received_date']
