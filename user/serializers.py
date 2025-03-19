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


class CustomerLinkSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    display_name = serializers.SerializerMethodField()

    def get_display_name(self, obj):
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name} - {obj.username}"
        return f"کاربر - {obj.username}"
