from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Appointment, Review
from .serializers import AppointmentSerializer, ReviewSerializer
from users.models import Doctor, Patient

class AppointmentViewSet(viewsets.ModelViewSet):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Appointment.objects.filter(doctor__user=user)
        elif user.role == 'PATIENT':
            return Appointment.objects.filter(patient__user=user)
        return Appointment.objects.none()

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        user = request.user

        # If user is a patient, automatically set the patient field
        if user.role == 'PATIENT':
            try:
                patient = Patient.objects.get(user=user)
                data['patient'] = patient.id
            except Patient.DoesNotExist:
                return Response(
                    {'error': 'Patient profile not found'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Validate that the doctor exists
        try:
            doctor = Doctor.objects.get(id=data.get('doctor'))
        except Doctor.DoesNotExist:
            return Response(
                {'error': 'Doctor not found'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create the appointment
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        appointment = self.get_object()
        appointment.status = 'CANCELLED'
        appointment.save()
        return Response({'status': 'Appointment cancelled'})

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]