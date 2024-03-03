from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework import status
from rest_framework.validators import UniqueValidator

User = get_user_model()


# Serializer to Register User
class CartUpdateSerializer(serializers.Serializer):

    pk = serializers.IntegerField(required=True)
    flag = serializers.BooleanField(required=False)
