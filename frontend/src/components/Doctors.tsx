import React, { useState, useEffect } from 'react';
import Table from './Table';
import EntityForm from './EntityForm';
import api from '../api/config';

interface Doctor {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  specialization: string;
  experience_years: number;
  qualification: string;
  consultation_fee: number;
  available_days: string[];
  available_times: string[];
}

const Doctors: React.FC = () => {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingDoctor, setEditingDoctor] = useState<any | null>(null);
  const [isEdit, setIsEdit] = useState(false);

  const fetchDoctors = async () => {
    try {
      const response = await api.get('/api/doctors/');
      const data = Array.isArray(response.data) ? response.data : response.data.results || response.data;
      const doctors = data.map((doctor: any) => ({
        id: doctor.id,
        first_name: doctor.user?.first_name,
        last_name: doctor.user?.last_name,
        email: doctor.user?.email,
        phone: doctor.user?.phone || '',
        specialization: doctor.specialization,
        experience_years: doctor.experience_years,
        qualification: doctor.qualification,
        consultation_fee: doctor.consultation_fee,
        available_days: doctor.available_days,
        available_times: doctor.available_times,
      }));
      setDoctors(doctors);
    } catch (error) {
      console.error('Error fetching doctors:', error);
    }
  };

  useEffect(() => {
    fetchDoctors();
  }, []);

  const handleSubmit = async (data: any) => {
    try {
      const payload = {
        user: {
          email: data.email,
          password: data.password,
          first_name: data.first_name,
          last_name: data.last_name,
        },
        specialization: data.specialization,
        experience_years: data.experience_years,
        qualification: data.qualification,
        consultation_fee: data.consultation_fee,
        available_days: data.available_days ? data.available_days.split(',').map((d: string) => d.trim()) : [],
        available_times: data.available_times ? data.available_times.split(',').map((t: string) => t.trim()) : [],
      };
      const url = editingDoctor
        ? `/api/doctors/${editingDoctor.id}/`
        : '/api/doctors/';
      const method = editingDoctor ? 'put' : 'post';
      if (editingDoctor) {
        // Remove password for edit if not changed
        delete payload.user.password;
      }
      await api[method](url, payload);
      fetchDoctors();
      setShowForm(false);
      setEditingDoctor(null);
      setIsEdit(false);
    } catch (error) {
      console.error('Error saving doctor:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this doctor?')) {
      try {
        await api.delete(`/api/doctors/${id}/`);
        fetchDoctors();
      } catch (error) {
        console.error('Error deleting doctor:', error);
      }
    }
  };

  const handleEdit = (doctor: any) => {
    setEditingDoctor({
      first_name: doctor.first_name || '',
      last_name: doctor.last_name || '',
      email: doctor.email || '',
      password: '', // always blank for edit
      specialization: doctor.specialization || '',
      experience_years: doctor.experience_years || '',
      qualification: doctor.qualification || '',
      consultation_fee: doctor.consultation_fee || '',
      available_days: Array.isArray(doctor.available_days) ? doctor.available_days.join(', ') : '',
      available_times: Array.isArray(doctor.available_times) ? doctor.available_times.join(', ') : '',
      id: doctor.id,
    });
    setShowForm(true);
    setIsEdit(true);
  };

  const formFields = [
    { name: 'first_name', label: 'First Name', type: 'text', required: true },
    { name: 'last_name', label: 'Last Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'password', label: 'Password', type: 'password', required: !isEdit },
    { name: 'specialization', label: 'Specialization', type: 'text', required: true },
    { name: 'experience_years', label: 'Experience Years', type: 'number', required: true },
    { name: 'qualification', label: 'Qualification', type: 'text', required: true },
    { name: 'consultation_fee', label: 'Consultation Fee', type: 'number', required: true },
    { name: 'available_days', label: 'Available Days (comma separated)', type: 'text', required: false },
    { name: 'available_times', label: 'Available Times (comma separated)', type: 'text', required: false },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Doctors</h2>
        <button
          onClick={() => {
            setEditingDoctor(null);
            setShowForm(true);
            setIsEdit(false);
          }}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Add Doctor
        </button>
      </div>

      {showForm ? (
        <div className="mb-6">
          <EntityForm
            fields={formFields}
            initialData={editingDoctor || {}}
            onSubmit={handleSubmit}
            onCancel={() => {
              setShowForm(false);
              setEditingDoctor(null);
              setIsEdit(false);
            }}
          />
        </div>
      ) : null}

      <Table
        headers={['First Name', 'Last Name', 'Email', 'Specialization', 'Experience Years', 'Qualification', 'Consultation Fee', 'Available Days', 'Available Times']}
        data={doctors}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default Doctors; 