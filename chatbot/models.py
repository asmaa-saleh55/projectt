from django.db import models
from users.models import User

class ChatbotQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chatbot_queries')
    user_input = models.TextField()
    ai_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chatbot_queries'
        ordering = ['-created_at']

class MedicalDataset(models.Model):
    symptoms = models.TextField()
    diagnosis = models.TextField()
    specialist = models.CharField(max_length=100)
    response = models.TextField()
    
    class Meta:
        db_table = 'medical_dataset'