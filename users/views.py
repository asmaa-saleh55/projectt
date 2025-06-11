from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import User, Doctor, Patient, Message
from appointments.models import Appointment, Review
from chatbot.models import ChatbotQuery
from .serializers import UserSerializer, DoctorSerializer, PatientSerializer, ChangePasswordSerializer, MessageSerializer, CustomTokenObtainPairSerializer, UserBasicSerializer
from appointments.serializers import AppointmentSerializer, ReviewSerializer
import json
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from django.db.models import Q

User = get_user_model()

def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    Returns a dictionary containing access and refresh tokens.
    """
    try:
        refresh = RefreshToken.for_user(user)
        tokens = {
            'access': str(refresh.access_token),
            'refresh': str(refresh)
        }
        print("✅ Tokens generated successfully for user:", user.email)
        return tokens
    except Exception as e:
        print(f"❌ Token generation failed for user {user.email}: {str(e)}")
        return None

class DoctorRegistrationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def post(self, request):
        try:
            print("📝 Doctor registration request received:", {
                "full_name": request.data.get('full_name', ''),
                "email": request.data.get('email'),
                "has_license": bool(request.FILES.get('license'))
            })
            
            # Extract data from request
            full_name = request.data.get('full_name', '')
            email = request.data.get('email')
            password = request.data.get('password')
            license_file = request.FILES.get('license')

            # Create doctor data with nested user
            doctor_data = {
                'user': {
                    'username': email,  # Use email as username
                    'full_name': full_name,
                    'email': email,
                    'password': password
                },
                'license': license_file,
                'specialization': 'General Medicine',  # Default value
                'working_hours': '9am-5pm'  # Default value
            }

            # Validate and create doctor
            serializer = DoctorSerializer(data=doctor_data)
            if not serializer.is_valid():
                print("❌ Doctor registration validation failed:", serializer.errors)
                return Response({
                    'status': 'error',
                    'message': 'Invalid data provided',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            doctor = serializer.save()
            print("✅ Doctor created successfully:", doctor.user.email)
            
            # Generate tokens
            tokens = get_tokens_for_user(doctor.user)
            if not tokens:
                print("❌ Failed to generate tokens for doctor:", doctor.user.email)
                return Response({
                    'status': 'error',
                    'message': 'Failed to generate authentication tokens'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Prepare response data
            response_data = {
                'status': 'success',
                'message': 'User registered successfully',
                'data': {
                    'user': {
                        'id': doctor.user.id,
                        'username': doctor.user.username,
                        'full_name': doctor.user.full_name,
                        'email': doctor.user.email,
                        'role': doctor.user.role
                    },
                    'tokens': tokens
                }
            }
            
            print("✅ Doctor registration successful:", {
                "user": response_data['data']['user'],
                "tokens": { "access": "***", "refresh": "***" }
            })
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ Doctor registration error: {str(e)}")
            return Response({
                'status': 'error',
                'message': 'An error occurred during registration',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PatientRegistrationView(APIView):
    permission_classes = [AllowAny]
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    
    def post(self, request):
        try:
            print("📝 Patient registration request received:", {
                "full_name": request.data.get('full_name', ''),
                "email": request.data.get('email')
            })
            
            data = request.data
            # Accept flat structure from frontend
            full_name = data.get("full_name", "")
            email = data.get("email")
            password = data.get("password")
            
            user_data = {
                "username": email,  # Use email as username
                "full_name": full_name,
                "email": email,
                "password": password
            }
            patient_data = {"user": user_data}

            serializer = PatientSerializer(data=patient_data)
            if not serializer.is_valid():
                print("❌ Patient registration validation failed:", serializer.errors)
                return Response({
                    "status": "error",
                    "message": "Invalid data provided",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            patient = serializer.save()
            print("✅ Patient created successfully:", patient.user.email)
            
            # Generate tokens
            tokens = get_tokens_for_user(patient.user)
            if not tokens:
                print("❌ Failed to generate tokens for patient:", patient.user.email)
                return Response({
                    'status': 'error',
                    'message': 'Failed to generate authentication tokens'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Prepare response data
            response_data = {
                "status": "success",
                "message": "User registered successfully",
                "data": {
                    "user": {
                        "id": patient.user.id,
                        "username": patient.user.username,
                        "full_name": patient.user.full_name,
                        "email": patient.user.email,
                        "role": patient.user.role
                    },
                    "tokens": tokens
                }
            }
            
            print("✅ Patient registration successful:", {
                "user": response_data['data']['user'],
                "tokens": { "access": "***", "refresh": "***" }
            })
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"❌ Patient registration error: {str(e)}")
            return Response({
                "status": "error",
                "message": "An error occurred during registration",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email')
            password = request.data.get('password')

            if not email or not password:
                return Response({
                    'status': 'error',
                    'message': 'Email and password are required',
                    'errors': {
                        'email': 'Email is required' if not email else None,
                        'password': 'Password is required' if not password else None
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({
                    'status': 'error',
                    'message': 'Invalid credentials',
                    'errors': {
                        'email': 'No user found with this email'
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)

            if not user.check_password(password):
                return Response({
                    'status': 'error',
                    'message': 'Invalid credentials',
                    'errors': {
                        'password': 'Invalid password'
                    }
                }, status=status.HTTP_401_UNAUTHORIZED)

            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            response_data = {
                'status': 'success',
                'message': 'Login successful',
                'data': {
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'email': user.email,
                        'role': user.role,
                        'address': user.address,
                        'about_me': user.about_me
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token)
                    }
                }
            }

            # Add doctor-specific data if user is a doctor
            if user.role == 'DOCTOR':
                try:
                    doctor = Doctor.objects.get(user=user)
                    response_data['data']['doctor'] = {
                        'id': doctor.id,
                        'specialization': doctor.specialization,
                        'working_hours': doctor.working_hours,
                        'verification_status': doctor.verification_status
                    }
                except Doctor.DoesNotExist:
                    pass

            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': 'An error occurred during login',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    @action(detail=False, methods=['get'], permission_classes=[IsAdminUser], url_path='admin-users')
    def admin_users(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['put'], permission_classes=[IsAdminUser], url_path='admin-verify')
    def admin_verify(self, request, pk=None):
        try:
            user = self.get_object()
            user.is_active = True  # Assuming 'is_active' is used for verification
            user.save()
            return Response({'message': f'User {user.email} verified successfully.'})
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

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

