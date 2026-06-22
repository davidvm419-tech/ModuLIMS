from rest_framework import serializers
from .models import User, UserTraceability


class UserAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'identification', 'email', 
                  'username', 'password', 'job_title', 'rol'
        ]

        # avoids sending the password to the frontend
        extra_kwargs = {'password': {'write_only': True}}

    def to_internal_value(self, data):
        '''
        cleans the data to avoid multiple names and white spaces.
        '''
        clean_data = data.copy()

        for key, value in clean_data.items():
            if isinstance(value, str):
                
                # avoid the password username and email to be normalized
                if key == 'password' or key == 'username' or key == 'email':
                    clean_data[key] = value.strip()
                else:
                    clean_data[key] = value.strip().upper()
                
        return super().to_internal_value(clean_data)


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'identification', 'password', 'sign']
        read_only_fields = ['first_name', 'last_name', 'username', 'identification']
        
        # avoids sending the password to the frontend
        extra_kwargs = {'password': {'write_only': True}}


class UserTraceabilitySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserTraceability
        fields = '__all__'
