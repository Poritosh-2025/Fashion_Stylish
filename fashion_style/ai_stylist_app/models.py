from django.db import models
from django.conf import settings
from uuid import uuid4
import json

class SessionHistory(models.Model):
    session_id = models.CharField(max_length=100, default=uuid4)
    user_id = models.CharField(max_length=100, blank=True, null=True)  # Can be User ID or anonymous session
    user_input = models.TextField()
    response = models.TextField()
    image = models.ImageField(upload_to='ai_images/', blank=True, null=True)
    analysis_data = models.JSONField(blank=True, null=True)  # Store outfit analysis JSON
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"Session {self.session_id} - {self.timestamp}"
    
    def get_analysis_data(self):
        """Return analysis data as dict"""
        if self.analysis_data:
            return self.analysis_data
        return {}

class OutfitAnalysis(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=100, default=uuid4)
    image = models.ImageField(upload_to='outfit_images/')
    title = models.CharField(max_length=100)
    colors = models.JSONField()  # Store colors as JSON array
    description = models.TextField()
    advice = models.TextField()
    bullet_advice = models.JSONField()  # Store bullet points as JSON array
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at}"
    
    def get_colors_display(self):
        """Return colors as comma-separated string"""
        if isinstance(self.colors, list):
            return ', '.join(self.colors)
        return str(self.colors)
    
    def get_bullet_advice_display(self):
        """Return bullet advice as formatted list"""
        if isinstance(self.bullet_advice, list):
            return self.bullet_advice
        return []
# from django.db import models

# class SessionHistory(models.Model):
#     user_id = models.CharField(max_length=100)  # Group records by user
#     user_input = models.TextField()
#     response = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)
#     image = models.ImageField(upload_to='outfit_images/', null=True, blank=True)

#     class Meta:
#         ordering = ['timestamp']

#     def __str__(self):
#         return f"{self.user_id} - {self.timestamp}"
