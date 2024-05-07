from rest_framework import serializers
from .models import *
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password


class UserRegistrationSerializer(serializers.ModelSerializer):
    is_staff = models.BooleanField(default=False)

    class Meta:
        model = UserProfile
        fields = ('id', 'first_name', 'last_name','username', 'email', 'password',"is_approved",'is_staff')
        extra_kwargs = {
            'password': {'write_only': True},
            'otp': {'required': False},
            'otp_verified': {'required': False},
            'date_of_birth': {'required': False},
            'address': {'required': False},
            'phone_number': {'required': False},
            'gender': {'required': False},
            'occupation': {'required': False},
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        user = UserProfile.objects.create(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    extra_kwargs = {}


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'username', 'email']


class UserUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'first_name', 'last_name', 'date_of_birth','occupation','gender', 'address', 'phone_number']

 
class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class BudgetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Budget
        exclude = ['user']


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goal
        exclude = ['user']