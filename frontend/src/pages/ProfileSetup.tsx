import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import api from '../api/config';

interface DoctorProfileData {
  specialization: string;
  experienceYears: number;
  qualification: string;
  consultationFee: number;
  availableDays: string[];
  availableTimes: string[];
}

interface PatientProfileData {
  dateOfBirth?: string;
  bloodGroup?: string;
  medicalHistory?: string;
}

const ProfileSetup: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const [doctorProfile, setDoctorProfile] = useState<DoctorProfileData>({
    specialization: '',
    experienceYears: 0,
    qualification: '',
    consultationFee: 0,
    availableDays: [],
    availableTimes: []
  });

  const [patientProfile, setPatientProfile] = useState<PatientProfileData>({
    dateOfBirth: '',
    bloodGroup: '',
    medicalHistory: ''
  });

  const handleDoctorChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setDoctorProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleMultiSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name } = e.target;
    const values = Array.from(e.target.selectedOptions, option => option.value);
    setDoctorProfile(prev => ({
      ...prev,
      [name]: values
    }));
  };

  const handlePatientChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setPatientProfile(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (user?.role === 'DOCTOR') {
        await api.post(`/api/users/doctors/`, {
          user: user.id,
          specialization: doctorProfile.specialization,
          experience_years: doctorProfile.experienceYears,
          qualification: doctorProfile.qualification,
          consultation_fee: doctorProfile.consultationFee,
          available_days: doctorProfile.availableDays,
          available_times: doctorProfile.availableTimes
        });
      } else if (user?.role === 'PATIENT') {
        await api.post(`/api/users/patients/`, {
          user: user.id,
          date_of_birth: patientProfile.dateOfBirth,
          blood_group: patientProfile.bloodGroup,
          medical_history: patientProfile.medicalHistory
        });
      }
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to create profile');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return <div>Please log in to continue.</div>;
  }

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md mx-auto">
        <div className="text-center">
          <h2 className="text-3xl font-extrabold text-gray-900">Complete Your Profile</h2>
          <p className="mt-2 text-sm text-gray-600">
            Please provide the required information to complete your {user.role.toLowerCase()} profile
          </p>
        </div>

        {error && (
          <div className="mt-4 bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="mt-8 space-y-6">
          {user.role === 'DOCTOR' ? (
            <>
              <div>
                <label htmlFor="specialization" className="block text-sm font-medium text-gray-700">
                  Specialization
                </label>
                <input
                  type="text"
                  id="specialization"
                  name="specialization"
                  required
                  value={doctorProfile.specialization}
                  onChange={handleDoctorChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="qualification" className="block text-sm font-medium text-gray-700">
                  Qualification
                </label>
                <input
                  type="text"
                  id="qualification"
                  name="qualification"
                  required
                  value={doctorProfile.qualification}
                  onChange={handleDoctorChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label htmlFor="experienceYears" className="block text-sm font-medium text-gray-700">
                    Years of Experience
                  </label>
                  <input
                    type="number"
                    id="experienceYears"
                    name="experienceYears"
                    required
                    min="0"
                    value={doctorProfile.experienceYears}
                    onChange={handleDoctorChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label htmlFor="consultationFee" className="block text-sm font-medium text-gray-700">
                    Consultation Fee
                  </label>
                  <input
                    type="number"
                    id="consultationFee"
                    name="consultationFee"
                    required
                    min="0"
                    value={doctorProfile.consultationFee}
                    onChange={handleDoctorChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>
              </div>

              <div>
                <label htmlFor="availableDays" className="block text-sm font-medium text-gray-700">
                  Available Days
                </label>
                <select
                  id="availableDays"
                  name="availableDays"
                  multiple
                  required
                  value={doctorProfile.availableDays}
                  onChange={handleMultiSelect}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="Monday">Monday</option>
                  <option value="Tuesday">Tuesday</option>
                  <option value="Wednesday">Wednesday</option>
                  <option value="Thursday">Thursday</option>
                  <option value="Friday">Friday</option>
                  <option value="Saturday">Saturday</option>
                  <option value="Sunday">Sunday</option>
                </select>
              </div>

              <div>
                <label htmlFor="availableTimes" className="block text-sm font-medium text-gray-700">
                  Available Times
                </label>
                <select
                  id="availableTimes"
                  name="availableTimes"
                  multiple
                  required
                  value={doctorProfile.availableTimes}
                  onChange={handleMultiSelect}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="09:00">09:00 AM</option>
                  <option value="10:00">10:00 AM</option>
                  <option value="11:00">11:00 AM</option>
                  <option value="12:00">12:00 PM</option>
                  <option value="14:00">02:00 PM</option>
                  <option value="15:00">03:00 PM</option>
                  <option value="16:00">04:00 PM</option>
                  <option value="17:00">05:00 PM</option>
                </select>
              </div>
            </>
          ) : (
            <>
              <div>
                <label htmlFor="dateOfBirth" className="block text-sm font-medium text-gray-700">
                  Date of Birth
                </label>
                <input
                  type="date"
                  id="dateOfBirth"
                  name="dateOfBirth"
                  value={patientProfile.dateOfBirth}
                  onChange={handlePatientChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="bloodGroup" className="block text-sm font-medium text-gray-700">
                  Blood Group
                </label>
                <select
                  id="bloodGroup"
                  name="bloodGroup"
                  value={patientProfile.bloodGroup}
                  onChange={handlePatientChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="">Select Blood Group</option>
                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>
                </select>
              </div>

              <div>
                <label htmlFor="medicalHistory" className="block text-sm font-medium text-gray-700">
                  Medical History
                </label>
                <textarea
                  id="medicalHistory"
                  name="medicalHistory"
                  rows={4}
                  value={patientProfile.medicalHistory}
                  onChange={handlePatientChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className={`w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 ${
                loading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {loading ? 'Saving...' : 'Complete Profile Setup'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default ProfileSetup; 