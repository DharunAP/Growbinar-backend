from rest_framework import serializers
from core.models import Mentee,Mentor

class UserSerializer(serializers.Serializer):
    email_id = serializers.EmailField()
    password = serializers.CharField(max_length=100)

class MentorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentor
        exclude = ['email_id','password','is_top_rated','is_experience']

class MenteeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentee
        exclude = ['email_id','password']