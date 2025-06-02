from django.shortcuts import render

# Create your views here.
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .models import ConversationHistory, OutfitSuggestion, ImageAnalysis
from .serializers import (
    ConversationHistorySerializer, OutfitSuggestionSerializer,
    OutfitRequestSerializer, ImageAnalysisSerializer, ChatMessageSerializer
)
from .ai_utils import FashionAI
import json

User = get_user_model()

# Initialize AI
fashion_ai = FashionAI()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_outfit(request):
    """Generate outfit suggestions based on user preferences"""
    
    serializer = OutfitRequestSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    
    # Generate outfit suggestion using AI
    outfit_description = fashion_ai.get_outfit_suggestion(
        occasion=data['occasion'],
        style_preference=data['style_preference'],
        weather=data.get('weather'),
        color_preference=data.get('color_preference'),
        additional_info=data.get('additional_info')
    )
    
    # Save to database
    outfit = OutfitSuggestion.objects.create(
        user=request.user,
        occasion=data['occasion'],
        style_preference=data['style_preference'],
        weather=data.get('weather', ''),
        color_preference=data.get('color_preference', ''),
        outfit_description=outfit_description
    )
    
    # Update user profile
    fashion_ai.update_user_profile(request.user, None, outfit)
    
    serializer = OutfitSuggestionSerializer(outfit)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat_with_ai(request):
    """Chat with AI fashion stylist"""
    
    serializer = ChatMessageSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user_message = serializer.validated_data['message']
    
    # Get conversation history for context
    conversation_history = ConversationHistory.objects.filter(
        user=request.user
    ).order_by('-created_at')[:5]
    
    # Generate AI response
    ai_response = fashion_ai.chat_with_stylist(user_message, conversation_history)
    
    # Save conversation
    conversation = ConversationHistory.objects.create(
        user=request.user,
        user_message=user_message,
        ai_response=ai_response
    )
    
    # Update user profile
    fashion_ai.update_user_profile(request.user, conversation, None)
    
    serializer = ConversationHistorySerializer(conversation)
    return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_image(request):
    """Analyze fashion image and provide suggestions"""
    
    serializer = ImageAnalysisSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Save image first
    image_analysis = ImageAnalysis.objects.create(
        user=request.user,
        image=serializer.validated_data['image']
    )
    
    # Analyze image using AI
    analysis_result = fashion_ai.analyze_fashion_image(image_analysis.image.path)
    suggestions = "Based on the analysis: " + analysis_result
    
    # Update the analysis
    image_analysis.analysis_result = analysis_result
    image_analysis.suggestions = suggestions
    image_analysis.save()
    
    result_serializer = ImageAnalysisSerializer(image_analysis)
    return Response(result_serializer.data, status=status.HTTP_201_CREATED)

class UserConversationHistoryView(generics.ListAPIView):
    """Get user's conversation history"""
    serializer_class = ConversationHistorySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ConversationHistory.objects.filter(user=self.request.user)

class UserOutfitSuggestionsView(generics.ListAPIView):
    """Get user's outfit suggestions"""
    serializer_class = OutfitSuggestionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return OutfitSuggestion.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_outfit(request, outfit_id):
    """Toggle favorite status of an outfit"""
    try:
        outfit = OutfitSuggestion.objects.get(id=outfit_id, user=request.user)
        outfit.is_favorite = not outfit.is_favorite
        outfit.save()
        
        # Update user profile
        fashion_ai.update_user_profile(request.user, None, outfit)
        
        serializer = OutfitSuggestionSerializer(outfit)
        return Response(serializer.data)
    except OutfitSuggestion.DoesNotExist:
        return Response(
            {'error': 'Outfit not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_ai_profile(request):
    """Get user's AI interaction summary"""
    user = request.user
    
    # Parse JSON data from user fields
    conversations = json.loads(user.conversation) if user.conversation else []
    outfits = json.loads(user.outfits) if user.outfits else []
    
    # Get statistics
    total_conversations = ConversationHistory.objects.filter(user=user).count()
    total_outfits = OutfitSuggestion.objects.filter(user=user).count()
    favorite_outfits = OutfitSuggestion.objects.filter(user=user, is_favorite=True).count()
    
    return Response({
        'user_id': user.id,
        'email': user.email,
        'total_conversations': total_conversations,
        'total_outfits': total_outfits,
        'favorite_outfits': favorite_outfits,
        'recent_conversations': conversations[-5:],  # Last 5 conversations
        'recent_outfits': outfits[-5:],  # Last 5 outfits
    })