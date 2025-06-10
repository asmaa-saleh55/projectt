from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from .models import ChatbotQuery, MedicalDataset
from .serializers import ChatbotQuerySerializer

class ChatbotViewSet(viewsets.ModelViewSet):
    queryset = ChatbotQuery.objects.all()
    serializer_class = ChatbotQuerySerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['post'])
    def ask(self, request):
        user_input = request.data.get('query', '')
        
        # Get all medical dataset entries
        medical_data = MedicalDataset.objects.all()
        corpus = [data.symptoms for data in medical_data]
        
        # Create TF-IDF vectorizer
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(corpus)
        
        # Transform user input
        user_vector = vectorizer.transform([user_input])
        
        # Calculate similarity
        similarities = cosine_similarity(user_vector, tfidf_matrix)
        most_similar_idx = np.argmax(similarities)
        
        # Get response from dataset
        response = medical_data[most_similar_idx].response
        specialist = medical_data[most_similar_idx].specialist
        
        # Save the interaction
        ChatbotQuery.objects.create(
            user=request.user,
            user_input=user_input,
            ai_response=response
        )
        
        return Response({
            'response': response,
            'recommended_specialist': specialist
        })