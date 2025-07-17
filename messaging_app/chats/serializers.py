from models import *
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    class meta:
        model = User
        fields = ['id', 'username', 'email', 'bio',]