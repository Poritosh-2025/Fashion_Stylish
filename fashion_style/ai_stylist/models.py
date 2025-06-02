from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ConversationHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_conversations')
    user_message = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at}"

class OutfitSuggestion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_outfits')
    occasion = models.CharField(max_length=100)
    style_preference = models.CharField(max_length=100)
    weather = models.CharField(max_length=50, blank=True)
    color_preference = models.CharField(max_length=100, blank=True)
    outfit_description = models.TextField()
    image_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_favorite = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.occasion}"

class ImageAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='image_analyses')
    image = models.ImageField(upload_to='fashion_images/')
    analysis_result = models.TextField()
    suggestions = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.email} - Image Analysis"