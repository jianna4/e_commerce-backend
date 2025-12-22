from rest_framework import serializers
from .models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    initials = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['email', 'full_name', 'password']
    
    def get_initials(self,obj):
        if obj.full_name:
          names= obj.full_name.strip().split()
          return ''.join([name[0].upper() for name in names[:2]])
        return obj.email[0].upper()


    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
