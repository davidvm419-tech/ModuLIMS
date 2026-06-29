from rest_framework  import  serializers
from .models import Assay, AssayTraceability, SampleAssay 


class  AssaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Assay
        fields =  '__all__'
    
    def to_internal_value(self, data):
        '''
        cleans the data to avoid multiple names of the same assay and white spaces.
        '''
        clean_data = data.copy()

        for key, value in clean_data.items():
            if isinstance(value, str):
                clean_data[key]  =  value.strip().upper()

        return super().to_internal_value(clean_data)
    

class AssayTraceabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model =  AssayTraceability
        fields = '__all__'


class SampleAssaySerializer(serializers.ModelSerializer):
    class Meta:
        model =  SampleAssay
        fields = '__all__'
        
        # if a duplicated assay tries to be added, return and error directly
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=SampleAssay.objects.all(),
                fields=['sample', 'assay'],
                message="Este ensayo ya fue asignado a esta muestra."
            )
        ]