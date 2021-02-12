from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from .models import CustomUser as User, LoginAdmin


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'fullname',
                  'profile',
                  'email_validation')


class RegisterSerializer(serializers.ModelSerializer):

    email = serializers.EmailField(
        validators=[UniqueValidator(User.objects.all())]
    )

    class Meta:
        model = User
        fields = ('id',
                  'email',
                  'password',
                  'fullname')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data['email'],
            validated_data['password'],
            validated_data['fullname'],
        )

        return user


class LoginSerializer(serializers.Serializer):

    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")


class CreateLoginAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoginAdmin
        fields = ('id',
                  'user',
                  'created_at',
                  'valid_until')


class UpdateLoginAdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = LoginAdmin
        fields = ('id', 'active')


class PinValidationSerializer(serializers.Serializer):

    pin = serializers.CharField(max_length=6)
