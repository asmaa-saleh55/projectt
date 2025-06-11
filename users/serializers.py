from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Doctor, Patient, Message, Hospital

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role')
        extra_kwargs = {
            'password': {'write_only': True},
            'full_name': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            full_name=validated_data['full_name'],
            password=validated_data['password']
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    doctor_profile = serializers.SerializerMethodField()
    patient_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'full_name', 'role', 'phone', 'address', 'is_superuser', 'is_staff',
                 'doctor_profile', 'patient_profile')
        extra_kwargs = {
            'full_name': {'required': True},
            'email': {'required': True},
            'password': {'write_only': True, 'required': True},
            'confirm_password': {'write_only': True, 'required': True}
        }

    def get_doctor_profile(self, obj):
        if hasattr(obj, 'doctor_profile'):
            return DoctorBasicSerializer(obj.doctor_profile).data
        return None

    def get_patient_profile(self, obj):
        if hasattr(obj, 'patient_profile'):
            return PatientBasicSerializer(obj.patient_profile).data
        return None

    def validate(self, attrs):
        if attrs['password'] != attrs.pop('confirm_password'):
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('confirm_password')
        role = validated_data.pop('role')
        password = validated_data.pop('password')

        user = User.objects.create(
            **validated_data
        )
        user.set_password(password)
        user.role = role # Assign role after setting password if it's part of initial user creation
        user.save()

        if role == 'DOCTOR':
            Doctor.objects.create(user=user)
        elif role == 'PATIENT':
            Patient.objects.create(user=user)
            
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        confirm_password = validated_data.pop('confirm_password', None)
        role = validated_data.pop('role', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
        
        if role:
            instance.role = role

        instance.save()

        # Handle doctor/patient profile creation if role changes
        if role and not hasattr(instance, 'doctor_profile') and role == 'DOCTOR':
            Doctor.objects.create(user=instance)
        elif role and not hasattr(instance, 'patient_profile') and role == 'PATIENT':
            Patient.objects.create(user=instance)

        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

class DoctorBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'specialty', 'medical_license', 'working_hours', 'certificates', 'about_me', 'education', 'experience', 'consultation_fee', 'rating', 'total_ratings', 'available_days', 'available_times')

class PatientBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'age', 'gender', 'date_of_birth', 'blood_group', 'medical_history')

class DoctorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()
    license = serializers.FileField(
        required=True,
        error_messages={
            'required': 'Medical license is required'
        }
    )
    specialization = serializers.CharField(required=False, default='General Medicine')
    working_hours = serializers.CharField(required=False, default='9am-5pm')
    certificates = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = Doctor
        fields = ('id', 'user', 'license', 'specialization', 'working_hours', 'certificates', 'verification_status')
        read_only_fields = ('id', 'verification_status')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserBasicSerializer(data=user_data)
        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)
        
        user = user_serializer.save()
        user.role = 'DOCTOR'
        user.save()
        
        doctor = Doctor.objects.create(user=user, **validated_data)
        return doctor

class PatientSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer()

    class Meta:
        model = Patient
        fields = ('id', 'user')
        read_only_fields = ('id',)

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = UserBasicSerializer(data=user_data)
        if not user_serializer.is_valid():
            raise serializers.ValidationError(user_serializer.errors)
        
        user = user_serializer.save()
        user.role = 'PATIENT'
        user.save()
        
        patient = Patient.objects.create(user=user)
        return patient

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'

class HospitalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hospital
        fields = ('id', 'name', 'address')