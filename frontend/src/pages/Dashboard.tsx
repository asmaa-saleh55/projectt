import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/config';

interface DoctorProfile {
  specialization: string;
  experienceYears: number;
  qualification: string;
  consultationFee: number;
  availableDays: string[];
  availableTimes: string[];
}

interface PatientProfile {
  dateOfBirth?: string;
  bloodGroup?: string;
  medicalHistory?: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState<DoctorProfile | PatientProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        if (!user?.id) {
          throw new Error('User ID not found');
        }

        let endpoint = '';
        if (user.role === 'DOCTOR') {
          endpoint = `/api/users/doctors/${user.id}/`;
        } else if (user.role === 'PATIENT') {
          endpoint = `/api/users/patients/${user.id}/`;
        } else if (user.isSuperuser || user.isStaff) {
          navigate('/admin-panel');
          return;
        } else {
          throw new Error('Invalid user role');
        }

        try {
          const response = await api.get(endpoint);
          const transformedProfile = {
            ...response.data,
            experienceYears: response.data.experience_years,
            consultationFee: response.data.consultation_fee,
            availableDays: response.data.available_days,
            availableTimes: response.data.available_times,
            dateOfBirth: response.data.date_of_birth,
            bloodGroup: response.data.blood_group,
            medicalHistory: response.data.medical_history
          };
          setProfile(transformedProfile);
        } catch (err: any) {
          if (err.response?.status === 404) {
            navigate('/profile-setup');
            return;
          }
          throw err;
        }
      } catch (err: any) {
        console.error('Failed to fetch profile:', err);
        setError(err.response?.data?.error || err.message || 'Failed to load profile');
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchProfile();
    }
  }, [user, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Loading your dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-red-600">{error}</p>
          <button 
            onClick={() => navigate('/profile-setup')} 
            className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Complete Profile Setup
          </button>
        </div>
      </div>
    );
  }

  const renderDoctorDashboard = (doctorProfile: DoctorProfile) => (
    <div className="space-y-4">
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold mb-4">Professional Information</h2>
        <div className="grid gap-4">
          <p><span className="font-medium">Specialization:</span> {doctorProfile.specialization}</p>
          <p><span className="font-medium">Experience:</span> {doctorProfile.experienceYears} years</p>
          <p><span className="font-medium">Qualification:</span> {doctorProfile.qualification}</p>
          <p><span className="font-medium">Consultation Fee:</span> ${doctorProfile.consultationFee}</p>
        </div>
      </div>
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold mb-4">Availability</h2>
        <div className="grid gap-4">
          <p><span className="font-medium">Available Days:</span> {doctorProfile.availableDays.join(', ')}</p>
          <p><span className="font-medium">Available Times:</span> {doctorProfile.availableTimes.join(', ')}</p>
        </div>
      </div>
    </div>
  );

  const renderPatientDashboard = (patientProfile: PatientProfile) => (
    <div className="space-y-4">
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-2xl font-semibold mb-4">Medical Information</h2>
        <div className="grid gap-4">
          {patientProfile.dateOfBirth && (
            <p><span className="font-medium">Date of Birth:</span> {patientProfile.dateOfBirth}</p>
          )}
          {patientProfile.bloodGroup && (
            <p><span className="font-medium">Blood Group:</span> {patientProfile.bloodGroup}</p>
          )}
          {patientProfile.medicalHistory && (
            <div>
              <p className="font-medium mb-2">Medical History:</p>
              <p className="bg-gray-50 p-4 rounded">{patientProfile.medicalHistory}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome, {user?.firstName}!
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            You are logged in as {user?.role.toLowerCase()}
          </p>
        </div>

        {profile && user?.role === 'DOCTOR' && renderDoctorDashboard(profile as DoctorProfile)}
        {profile && user?.role === 'PATIENT' && renderPatientDashboard(profile as PatientProfile)}
      </div>
    </div>
  );
};

export default Dashboard; 