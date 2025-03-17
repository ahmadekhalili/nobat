import jwt
from django.conf import settings
from rest_framework import serializers
from .models import *


class StateSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=150)

    class Meta:
        model = State
        fields = ['id', 'name']


class TownSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=150)

    state = StateSerializer()  # Nested serializer for State

    class Meta:
        model = Town
        fields = ['id', 'name', 'state']


class ServiceTypeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField()
    name = serializers.CharField(max_length=150)

    class Meta:
        model = ServiceType
        fields = ['id', 'name']
