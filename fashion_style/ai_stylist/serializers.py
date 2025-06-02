from rest_framework import serializers
from .models import ConversationHistory, OutfitSuggestion, ImageAnalysis

class ConversationHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationHistory
        fields = ['id', 'user_message', 'ai_response', 'created_at']
        read_only_fields = ['id', 'created_at']

class OutfitSuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = OutfitSuggestion
        fields = [
            'id', 'occasion', 'style_preference', 'weather', 
            'color_preference', 'outfit_description', 'image_url',
            'created_at', 'is_favorite'
        ]
        read_only_fields = ['id', 'created_at']

class OutfitRequestSerializer(serializers.Serializer):
    occasion = serializers.CharField(max_length=100)
    style_preference = serializers.CharField(max_length=100)
    weather = serializers.CharField(max_length=50, required=False)
    color_preference = serializers.CharField(max_length=100, required=False)
    additional_info = serializers.CharField(required=False)

class ImageAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageAnalysis
        fields = ['id', 'image', 'analysis_result', 'suggestions', 'created_at']
        read_only_fields = ['id', 'analysis_result', 'suggestions', 'created_at']

class ChatMessageSerializer(serializers.Serializer):
    message = serializers.CharField()