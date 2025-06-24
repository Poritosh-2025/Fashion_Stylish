from django.urls import path
from .views import OutfitAnalysisView, TextQueryView

app_name = 'ai_stylist'

urlpatterns = [
    path('analyze-outfit/', OutfitAnalysisView.as_view(), name='analyze-outfit'),
    path('text-query/', TextQueryView.as_view(), name='text-query'),
]