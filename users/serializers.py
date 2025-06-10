from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User, Doctor, Patient, Message

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    is_superuser = serializers.BooleanField(read_only=True)
    is_staff = serializers.BooleanField(read_only=True)
    doctor_profile = serializers.SerializerMethodField()
    patient_profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'confirm_password', 
                 'first_name', 'last_name', 'role', 'phone', 'address', 'is_superuser', 'is_staff',
                 'doctor_profile', 'patient_profile')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True}
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
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role=validated_data['role'],
            phone=validated_data.get('phone', ''),
            address=validated_data.get('address', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_new_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_new_password']:
            raise serializers.ValidationError({"new_password": "Password fields didn't match."})
        return attrs

class UserBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'phone')

class DoctorBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Doctor
        fields = ('id', 'specialization', 'experience_years', 'qualification', 'consultation_fee', 'available_days', 'available_times')

class PatientBasicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ('id', 'date_of_birth', 'blood_group', 'medical_history')

class DoctorSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Doctor
        fields = '__all__'

    def create(self, validated_data):
        user_data = self.initial_data.get('user')
        if user_data:
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role='DOCTOR'
            )
            validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = self.initial_data.get('user')
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr != 'password':
                    setattr(user, attr, value)
            if 'password' in user_data:
                user.set_password(user_data['password'])
            user.save()
        return super().update(instance, validated_data)

class PatientSerializer(serializers.ModelSerializer):
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Patient
        fields = '__all__'

    def create(self, validated_data):
        user_data = self.initial_data.get('user')
        if user_data:
            user = User.objects.create_user(
                username=user_data['email'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role='PATIENT'
            )
            validated_data['user'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user_data = self.initial_data.get('user')
        if user_data:
            user = instance.user
            for attr, value in user_data.items():
                if attr != 'password':
                    setattr(user, attr, value)
            if 'password' in user_data:
                user.set_password(user_data['password'])
            user.save()
        return super().update(instance, validated_data)

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'