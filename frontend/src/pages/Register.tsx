import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authService } from '../api/auth';

interface FormData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: 'doctor' | 'patient';
  specialization?: string;
  experienceYears?: number;
  qualification?: string;
  consultationFee?: number;
  availableDays?: string[];
  availableTimes?: string[];
  date_of_birth?: string;
  blood_group?: string;
  medical_history?: string;
}

const Register: React.FC = () => {
  const navigate = useNavigate();
  const [error, setError] = useState<string>('');
  const [formData, setFormData] = useState<FormData>({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    role: 'patient',
    specialization: '',
    experienceYears: undefined,
    qualification: '',
    consultationFee: undefined,
    availableDays: [],
    availableTimes: [],
    date_of_birth: '',
    blood_group: '',
    medical_history: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleMultiSelect = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name } = e.target;
    const values = Array.from(e.target.selectedOptions, option => option.value);
    setFormData(prev => ({
      ...prev,
      [name]: values
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      await authService.register(formData);
      navigate('/login');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
          Create your account
        </h2>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
          {error && (
            <div className="mb-4 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <form className="space-y-6" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="role" className="block text-sm font-medium text-gray-700">
                Role
              </label>
              <select
                id="role"
                name="role"
                value={formData.role}
                onChange={handleChange}
                className="mt-1 block w-full py-2 px-3 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              >
                <option value="patient">Patient</option>
                <option value="doctor">Doctor</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="firstName" className="block text-sm font-medium text-gray-700">
                  First Name
                </label>
                <input
                  type="text"
                  id="firstName"
                  name="firstName"
                  required
                  value={formData.firstName}
                  onChange={handleChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>

              <div>
                <label htmlFor="lastName" className="block text-sm font-medium text-gray-700">
                  Last Name
                </label>
                <input
                  type="text"
                  id="lastName"
                  name="lastName"
                  required
                  value={formData.lastName}
                  onChange={handleChange}
                  className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                />
              </div>
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700">
                Password
              </label>
              <input
                type="password"
                id="password"
                name="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            {formData.role === 'doctor' && (
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
                    value={formData.specialization}
                    onChange={handleChange}
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
                    value={formData.qualification}
                    onChange={handleChange}
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
                      value={formData.experienceYears}
                      onChange={handleChange}
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
                      value={formData.consultationFee}
                      onChange={handleChange}
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
                    value={formData.availableDays}
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
                    value={formData.availableTimes}
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
            )}

            {formData.role === 'patient' && (
              <>
                <div>
                  <label htmlFor="date_of_birth" className="block text-sm font-medium text-gray-700">
                    Date of Birth
                  </label>
                  <input
                    type="date"
                    id="date_of_birth"
                    name="date_of_birth"
                    value={formData.date_of_birth}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                  />
                </div>

                <div>
                  <label htmlFor="blood_group" className="block text-sm font-medium text-gray-700">
                    Blood Group
                  </label>
                  <select
                    id="blood_group"
                    name="blood_group"
                    value={formData.blood_group}
                    onChange={handleChange}
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
                  <label htmlFor="medical_history" className="block text-sm font-medium text-gray-700">
                    Medical History
                  </label>
                  <textarea
                    id="medical_history"
                    name="medical_history"
                    rows={4}
                    value={formData.medical_history}
                    onChange={handleChange}
                    className="mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
                    placeholder="Enter any relevant medical history..."
                  />
                </div>
              </>
            )}

            <div>
              <button
                type="submit"
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Register
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Register; 