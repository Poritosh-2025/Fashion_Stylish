from django.contrib import admin
from .models import ConversationHistory, OutfitSuggestion, ImageAnalysis

@admin.register(ConversationHistory)
class ConversationHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'user_message_preview']
    list_filter = ['created_at']
    search_fields = ['user__email', 'user_message']
    
    def user_message_preview(self, obj):
        return obj.user_message[:50] + "..." if len(obj.user_message) > 50 else obj.user_message
    user_message_preview.short_description = "Message Preview"

@admin.register(OutfitSuggestion)
class OutfitSuggestionAdmin(admin.ModelAdmin):
    list_display = ['user', 'occasion', 'style_preference', 'is_favorite', 'created_at']
    list_filter = ['occasion', 'style_preference', 'is_favorite', 'created_at']
    search_fields = ['user__email', 'occasion', 'style_preference']

@admin.register(ImageAnalysis)
class ImageAnalysisAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at', 'image']
    list_filter = ['created_at']
    search_fields = ['user__email']