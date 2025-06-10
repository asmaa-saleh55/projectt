from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import User, Doctor, Patient, Message
from appointments.models import Appointment, Review
from chatbot.models import ChatbotQuery
from .serializers import UserSerializer, DoctorSerializer, PatientSerializer, ChangePasswordSerializer, MessageSerializer
from appointments.serializers import AppointmentSerializer, ReviewSerializer
import json
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.db.models import Q

User = get_user_model()

@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register_user(request):
    data = request.data
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
    for field in required_fields:
        if field not in data:
            return Response(
                {'error': f'{field} is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Check if user already exists
    if User.objects.filter(email=data['email']).exists():
        return Response(
            {'error': 'User with this email already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate role
    if data['role'].upper() not in ['DOCTOR', 'PATIENT']:
        return Response(
            {'error': 'Invalid role. Must be either "doctor" or "patient"'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate doctor-specific fields if role is doctor
    if data['role'].upper() == 'DOCTOR':
        doctor_fields = ['specialization', 'experience_years', 'qualification', 
                        'consultation_fee', 'available_days', 'available_times']
        for field in doctor_fields:
            if field not in data:
                return Response(
                    {'error': f'{field} is required for doctors'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Validate experience_years is a number
        try:
            experience_years = int(data['experience_years'])
            if experience_years < 0:
                raise ValueError
        except ValueError:
            return Response(
                {'error': 'experience_years must be a positive number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate consultation_fee is a number
        try:
            consultation_fee = float(data['consultation_fee'])
            if consultation_fee < 0:
                raise ValueError
        except ValueError:
            return Response(
                {'error': 'consultation_fee must be a positive number'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate available_days and available_times are lists
        if not isinstance(data['available_days'], list) or not isinstance(data['available_times'], list):
            return Response(
                {'error': 'available_days and available_times must be lists'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    # Validate patient-specific fields if role is patient
    elif data['role'].upper() == 'PATIENT':
        patient_fields = {
            'date_of_birth': None,  # Optional
            'blood_group': None,    # Optional
            'medical_history': None # Optional
        }
        
        # Extract patient fields if they exist
        patient_data = {
            field: data.get(field)
            for field in patient_fields
            if field in data
        }
    
    try:
        # Create user with email as username
        user = User.objects.create_user(
            username=data['email'],  # Use email as username
            email=data['email'],
            password=data['password'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            role=data['role'].upper()
        )
        
        # Create doctor or patient profile
        if user.role == 'DOCTOR':
            doctor = Doctor.objects.create(
                user=user,
                specialization=data['specialization'],
                experience_years=int(data['experience_years']),
                qualification=data['qualification'],
                consultation_fee=float(data['consultation_fee']),
                available_days=data['available_days'],
                available_times=data['available_times']
            )
            # Add doctor profile to response
            doctor_serializer = DoctorSerializer(doctor)
            profile_data = doctor_serializer.data
        elif user.role == 'PATIENT':
            patient = Patient.objects.create(
                user=user,
                date_of_birth=data.get('date_of_birth'),
                blood_group=data.get('blood_group', ''),
                medical_history=data.get('medical_history', '')
            )
            # Add patient profile to response
            patient_serializer = PatientSerializer(patient)
            profile_data = patient_serializer.data
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'status': 'success',
            'message': 'Registration successful',
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            },
            'user': {
                'id': user.id,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.role,
                'profile': profile_data
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def login(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Please provide both username and password'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user:
            refresh = RefreshToken.for_user(user)
            serializer = self.get_serializer(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': serializer.data
            })
        
        return Response({
            'error': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def profile(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        
        partial = request.method == 'PATCH'
        serializer = self.get_serializer(request.user, data=request.data, partial=partial)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            if user.check_password(serializer.validated_data['old_password']):
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                return Response({'message': 'Password changed successfully'})
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def reset_password(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Please provide an email address'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            # Generate password reset token
            token = RefreshToken.for_user(user)
            
            # Send password reset email
            reset_url = f"https://your-frontend-url/reset-password?token={token}"
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_url}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=True,
            )
            return Response({'message': 'Password reset email sent'})
        except User.DoesNotExist:
            return Response({'error': 'No user found with this email address'}, 
                          status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            user = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

@method_decorator(csrf_exempt, name='dispatch')
class DoctorViewSet(viewsets.ModelViewSet):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        queryset = Doctor.objects.all()
        specialization = self.request.query_params.get('specialization', None)
        if specialization:
            queryset = queryset.filter(specialization__icontains=specialization)
        return queryset
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            doctor = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        self.perform_destroy(instance)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def availability(self, request, pk=None):
        doctor = self.get_object()
        return Response({
            'available_days': doctor.available_days,
            'available_times': doctor.available_times
        })
    
    @action(detail=True, methods=['post'])
    def update_availability(self, request, pk=None):
        doctor = self.get_object()
        if doctor.user != request.user and request.user.role != 'ADMIN':
            return Response({'error': 'Not authorized'}, status=status.HTTP_403_FORBIDDEN)
        
        doctor.available_days = request.data.get('available_days', doctor.available_days)
        doctor.available_times = request.data.get('available_times', doctor.available_times)
        doctor.save()
        return Response({
            'status': 'Availability updated',
            'available_days': doctor.available_days,
            'available_times': doctor.available_times
        })

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def appointments(self, request, pk=None):
        doctor = self.get_object()
        appointments = Appointment.objects.filter(doctor=doctor)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

@method_decorator(csrf_exempt, name='dispatch')
class PatientViewSet(viewsets.ModelViewSet):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def get_queryset(self):
        if self.request.user.role == 'DOCTOR':
            return Patient.objects.filter(appointments__doctor__user=self.request.user).distinct()
        elif self.request.user.role == 'PATIENT':
            return Patient.objects.filter(user=self.request.user)
        return Patient.objects.all()
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            patient = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if serializer.is_valid():
            patient = serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = instance.user
        self.perform_destroy(instance)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    """Get the current user's profile"""
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

# --- Logout API ---
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken, TokenError
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logout successful."}, status=status.HTTP_205_RESET_CONTENT)
        except TokenError as e:
            # Token is invalid or already blacklisted
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": "An unexpected error occurred: " + str(e)}, status=status.HTTP_400_BAD_REQUEST)

# --- Appointments ---
class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'doctor_profile'):
            return Appointment.objects.filter(doctor__user=user)
        elif hasattr(user, 'patient_profile'):
            return Appointment.objects.filter(patient__user=user)
        return Appointment.objects.none()

    @action(detail=False, methods=['post'], url_path='check-availability')
    def check_availability(self, request):
        doctor_id = request.data.get('doctor_id')
        date = request.data.get('appointment_date')
        time = request.data.get('appointment_time')
        exists = Appointment.objects.filter(
            doctor_id=doctor_id,
            appointment_date=date,
            appointment_time=time,
            status='CONFIRMED'
        ).exists()
        return Response({'available': not exists})

    @action(detail=True, methods=['patch'], url_path='status')
    def change_status(self, request, pk=None):
        appointment = self.get_object()
        status_value = request.data.get('status')
        if status_value not in ['CONFIRMED', 'CANCELLED', 'COMPLETED']:
            return Response({'error': 'Invalid status'}, status=400)
        appointment.status = status_value
        appointment.save()
        return Response({'status': appointment.status})

# --- Reviews ---
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='doctor/(?P<doctor_id>[^/.]+)')
    def doctor_reviews(self, request, doctor_id=None):
        reviews = Review.objects.filter(doctor_id=doctor_id)
        serializer = self.get_serializer(reviews, many=True)
        return Response(serializer.data)

# --- Messaging ---
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'], url_path='conversation/(?P<user_id>[^/.]+)')
    def conversation(self, request, user_id=None):
        user = request.user
        messages = Message.objects.filter(
            (Q(sender=user) & Q(receiver_id=user_id)) |
            (Q(sender_id=user_id) & Q(receiver=user))
        ).order_by('timestamp')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)

# --- Chatbot ---
class ChatbotAskView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        question = request.data.get('question')
        # Implement TF-IDF logic here, fallback to Gemini API if needed
        answer = "AI response here"  # Replace with actual logic
        return Response({'answer': answer})

# --- Admin Stats ---
class AdminStatsView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            'users': User.objects.count(),
            'appointments': Appointment.objects.count(),
            'reviews': Review.objects.count(),
        })

class DoctorPerformanceView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if not hasattr(user, 'doctor_profile'):
            return Response({'error': 'Not a doctor'}, status=403)
        from django.utils import timezone
        from datetime import timedelta
        start_week = timezone.now().date() - timedelta(days=timezone.now().weekday())
        end_week = start_week + timedelta(days=6)
        count = Appointment.objects.filter(
            doctor__user=user,
            appointment_date__range=[start_week, end_week]
        ).count()
        return Response({'patients_this_week': count})

