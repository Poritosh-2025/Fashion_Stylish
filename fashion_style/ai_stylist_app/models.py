from django.db import models

class SessionHistory(models.Model):
    user_id = models.CharField(max_length=100)  # Group records by user
    user_input = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to='outfit_images/', null=True, blank=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"{self.user_id} - {self.timestamp}"
