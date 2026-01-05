from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate


class RegistrationSerializer(serializers.ModelSerializer):

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_confirmed_password(self, value):
        """
        Ensures that the `confirmed_password` matches the provided `password`;
        raises a validation error if they differ.
        """
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value
    
    def validate_email(self, value):
        """
        Validates that the email address is unique; raises an error if a user
        with the given email already exists.
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Invalid credentials.')
        return value

    def create(self, validated_data):

        validated_data.pop('confirmed_password')
        validated_data['username'] = validated_data['email']
        user = User.objects.create_user(**validated_data)
        user.is_active = False 
        user.save()
        return user
    

class LoginTokenObtainPairSerializer(serializers.Serializer):
    
    email = serializers.CharField()
    password = serializers.CharField()

    def validate(self, payload):

        payload_email = payload.get('email')
        payload_password = payload.get('password')

        try:
            user = User.objects.get(username=payload_email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email or password is not correct")

        user = authenticate(username=payload_email, password=payload_password)
        if not user:
            raise serializers.ValidationError("Email or password is not correct")

        payload['user'] = user
        return payload