from rest_framework import serializers
from static.models import Testimonial

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'