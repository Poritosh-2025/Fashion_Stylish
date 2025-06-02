from django.urls import path
from . import views

app_name = 'ai_stylist'

urlpatterns = [
    path('generate-outfit/', views.generate_outfit, name='generate_outfit'),
    path('chat/', views.chat_with_ai, name='chat_with_ai'),
    path('analyze-image/', views.analyze_image, name='analyze_image'),
    path('conversations/', views.UserConversationHistoryView.as_view(), name='user_conversations'),
    path('outfits/', views.UserOutfitSuggestionsView.as_view(), name='user_outfits'),
    path('outfits/<int:outfit_id>/favorite/', views.toggle_favorite_outfit, name='toggle_favorite'),
    path('profile/', views.user_ai_profile, name='user_ai_profile'),
]