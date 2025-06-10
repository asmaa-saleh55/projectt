import React, { useState, useEffect } from 'react';
import Table from './Table';
import EntityForm from './EntityForm';
import api from '../api/config';

interface Patient {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone: string;
  date_of_birth: string;
  blood_group: string;
  medical_history: string;
}

const Patients: React.FC = () => {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingPatient, setEditingPatient] = useState<any | null>(null);
  const [isEdit, setIsEdit] = useState(false);

  const fetchPatients = async () => {
    try {
      const response = await api.get('/api/patients/');
      const data = Array.isArray(response.data) ? response.data : response.data.results || response.data;
      const patients = data.map((patient: any) => ({
        id: patient.id,
        first_name: patient.user?.first_name,
        last_name: patient.user?.last_name,
        email: patient.user?.email,
        phone: patient.user?.phone || '',
        date_of_birth: patient.date_of_birth || '',
        blood_group: patient.blood_group || '',
        medical_history: patient.medical_history || '',
      }));
      setPatients(patients);
    } catch (error) {
      console.error('Error fetching patients:', error);
    }
  };

  useEffect(() => {
    fetchPatients();
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
        date_of_birth: data.date_of_birth,
        blood_group: data.blood_group,
        medical_history: data.medical_history,
      };
      const url = editingPatient
        ? `/api/patients/${editingPatient.id}/`
        : '/api/patients/';
      const method = editingPatient ? 'put' : 'post';
      if (editingPatient) {
        delete payload.user.password;
      }
      await api[method](url, payload);
      fetchPatients();
      setShowForm(false);
      setEditingPatient(null);
      setIsEdit(false);
    } catch (error) {
      console.error('Error saving patient:', error);
    }
  };

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this patient?')) {
      try {
        await api.delete(`/api/patients/${id}/`);
        fetchPatients();
      } catch (error) {
        console.error('Error deleting patient:', error);
      }
    }
  };

  const handleEdit = (patient: any) => {
    setEditingPatient({
      first_name: patient.first_name || '',
      last_name: patient.last_name || '',
      email: patient.email || '',
      password: '',
      date_of_birth: patient.date_of_birth || '',
      blood_group: patient.blood_group || '',
      medical_history: patient.medical_history || '',
      id: patient.id,
    });
    setShowForm(true);
    setIsEdit(true);
  };

  const formFields = [
    { name: 'first_name', label: 'First Name', type: 'text', required: true },
    { name: 'last_name', label: 'Last Name', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'password', label: 'Password', type: 'password', required: !isEdit },
    { name: 'date_of_birth', label: 'Date of Birth', type: 'date', required: false },
    { name: 'blood_group', label: 'Blood Group', type: 'text', required: false },
    { name: 'medical_history', label: 'Medical History', type: 'text', required: false },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Patients</h2>
        <button
          onClick={() => {
            setEditingPatient(null);
            setShowForm(true);
            setIsEdit(false);
          }}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Add Patient
        </button>
      </div>

      {showForm ? (
        <div className="mb-6">
          <EntityForm
            fields={formFields}
            initialData={editingPatient || {}}
            onSubmit={handleSubmit}
            onCancel={() => {
              setShowForm(false);
              setEditingPatient(null);
              setIsEdit(false);
            }}
          />
        </div>
      ) : null}

      <Table
        headers={['First Name', 'Last Name', 'Email', 'Date of Birth', 'Blood Group', 'Medical History']}
        data={patients}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default Patients; 