from rest_framework import serializers
from .models import CustomUser
class UserRegisterationSerializer(serializers.ModelSerializer):
    password=serializers.CharField(write_only=True,min_length=8)
    confirm_password=serializers.CharField(write_only=True,min_length=8)
    class Meta:
        model=CustomUser
        fields=['email','fullname','password','confirm_password',"username"]

    def validate(self, data):
        if data["password"] !=data["confirm_password"]:
            raise serializers.ValidationError({"password":"password donot match"})
        return data

class LoginSerializer(serializers.Serializer):
    username=serializers.CharField(required=True)
    password=serializers.CharField(required=True,write_only=True)
