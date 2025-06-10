from rest_framework import serializers
from .models import ChatbotQuery, MedicalDataset

class ChatbotQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotQuery
        fields = '__all__'

class MedicalDatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalDataset
        fields = '__all__'