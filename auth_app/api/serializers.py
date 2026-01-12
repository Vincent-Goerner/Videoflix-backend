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
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value
    
    def validate_email(self, value):
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
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Email or password is not correct")

        if not user.is_active:
            raise serializers.ValidationError("Account is not activated")

        user = authenticate(username=user.username, password=password)
        if user is None:
            raise serializers.ValidationError("Email or password is not correct")

        data['user'] = user
        return data
    

class PasswordResetSerializer(serializers.Serializer):

    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):

    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."})
        return data