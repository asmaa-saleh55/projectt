from rest_framework import serializers
from .models import Appointment, Review
from users.serializers import DoctorSerializer, PatientSerializer
from users.models import Doctor, Patient
from datetime import datetime, time

class AppointmentSerializer(serializers.ModelSerializer):
    doctor_details = DoctorSerializer(source='doctor', read_only=True)
    patient_details = PatientSerializer(source='patient', read_only=True)
    date = serializers.DateField(source='appointment_date')
    time_slot = serializers.CharField(write_only=True)
    
    class Meta:
        model = Appointment
        fields = ['id', 'doctor', 'doctor_details', 'patient', 'patient_details', 
                 'date', 'time_slot', 'appointment_time', 'status', 'symptoms', 
                 'diagnosis', 'prescription', 'created_at', 'updated_at']
        read_only_fields = ['appointment_time', 'status', 'diagnosis', 'prescription']

    def validate(self, data):
        # Convert time_slot to appointment_time
        try:
            time_slot = data.pop('time_slot')
            start_time = time_slot.split('-')[0]
            data['appointment_time'] = datetime.strptime(start_time, '%H:%M').time()
        except (ValueError, IndexError):
            raise serializers.ValidationError({
                'time_slot': 'Invalid time slot format. Use HH:MM-HH:MM format (e.g., 09:00-09:30)'
            })

        # Validate that the appointment is not in the past
        appointment_date = data.get('appointment_date')
        if appointment_date < datetime.now().date():
            raise serializers.ValidationError({
                'date': 'Cannot create appointments in the past'
            })

        return data

    def create(self, validated_data):
        # Set initial status
        validated_data['status'] = 'PENDING'
        return super().create(validated_data)

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'