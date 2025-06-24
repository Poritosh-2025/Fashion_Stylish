from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import OutfitAnalysisRequestSerializer, OutfitAnalysisResponseSerializer, TextQueryRequestSerializer, SessionHistorySerializer
from .utils import analyze_outfit, handle_text_query, save_to_json
from .models import SessionHistory

class OutfitAnalysisView(APIView):
    def post(self, request):
        serializer = OutfitAnalysisRequestSerializer(data=request.data)
        if serializer.is_valid():
            image = serializer.validated_data['image']
            context = serializer.validated_data.get('context', '')
            user_id = serializer.validated_data['user_id']
            
            analysis = analyze_outfit(image, context, user_id)
            if not analysis:
                return Response({"error": "Could not analyze the outfit. Please try another image."}, status=status.HTTP_400_BAD_REQUEST)
            
            # Validate response
            response_serializer = OutfitAnalysisResponseSerializer(data=analysis)
            if not response_serializer.is_valid():
                return Response({"error": "Invalid analysis response format."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Save to session history with image and user_id
            SessionHistory.objects.create(
                user_id=user_id,
                user_input=f"upload (image) with context: {context}" if context else "upload (image)",
                response=analysis['advice'],
                image=image
            )
            
            # Save analysis to JSON file
            save_to_json(analysis)
            
            return Response(response_serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TextQueryView(APIView):
    def post(self, request):
        serializer = TextQueryRequestSerializer(data=request.data)
        if serializer.is_valid():
            query = serializer.validated_data['query']
            user_id = serializer.validated_data['user_id']
            
            response_text = handle_text_query(query, user_id)
            
            # Save to session history (no image for text queries)
            SessionHistory.objects.create(
                user_id=user_id,
                user_input=query,
                response=response_text
            )
            
            return Response({"response": response_text}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)