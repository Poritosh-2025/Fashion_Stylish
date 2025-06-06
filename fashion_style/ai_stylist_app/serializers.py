from rest_framework import serializers
from .models import SessionHistory

class OutfitAnalysisRequestSerializer(serializers.Serializer):
    image = serializers.ImageField()
    context = serializers.CharField(required=False, allow_blank=True)
    user_id = serializers.CharField(max_length=100)  # New field for user ID

class OutfitAnalysisResponseSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=50)
    colors = serializers.ListField(child=serializers.CharField())
    description = serializers.CharField()
    advice = serializers.CharField()

class TextQueryRequestSerializer(serializers.Serializer):
    query = serializers.CharField()
    user_id = serializers.CharField(max_length=100)  # New field for user ID

class SessionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionHistory
        fields = ['user_id', 'user_input', 'response', 'timestamp', 'image']