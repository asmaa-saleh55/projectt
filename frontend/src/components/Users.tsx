import React, { useState, useEffect } from 'react';
import Table from './Table';
import EntityForm from './EntityForm';
import api from '../api/config';

interface BackendUser {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  role?: string;
}

interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  isStaff: boolean;
}

const Users: React.FC = () => {
  const [users, setUsers] = useState<BackendUser[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingUser, setEditingUser] = useState<any | null>(null);
  const [isEdit, setIsEdit] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchUsers = async () => {
    try {
      const response = await api.get('/api/users/');
      let usersData = Array.isArray(response.data)
        ? response.data
        : response.data?.results || response.data;
      if (!Array.isArray(usersData)) usersData = [];
      setUsers(usersData);
    } catch (error) {
      setUsers([]);
      console.error('Failed to fetch users:', error);
    }
  };

  const handleEdit = (user: BackendUser) => {
    setEditingUser({
      ...user,
      firstName: user.first_name,
      lastName: user.last_name,
      isStaff: user.is_staff,
      password: '',
      confirm_password: '',
      role: user.role || 'PATIENT',
    });
    setShowForm(true);
    setIsEdit(true);
    setError(null);
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/api/users/${id}/`);
      fetchUsers();
    } catch (error: any) {
      setError(error?.response?.data?.error || 'Failed to delete user');
      console.error('Failed to delete user:', error);
    }
  };

  const handleSubmit = async (formData: any) => {
    try {
      setError(null);
      if (editingUser) {
        const payload: any = {
          ...formData,
          first_name: formData.firstName,
          last_name: formData.lastName,
          is_staff: formData.isStaff,
          role: formData.role || editingUser.role || 'PATIENT',
        };
        if (formData.password) {
          payload.password = formData.password;
          payload.confirm_password = formData.confirm_password;
        }
        await api.put(`/api/users/${editingUser.id}/`, payload);
      } else {
        await api.post('/api/users/', {
          ...formData,
          username: formData.username || formData.email,
          email: formData.email,
          first_name: formData.firstName,
          last_name: formData.lastName,
          is_staff: formData.isStaff,
          password: formData.password,
          confirm_password: formData.confirm_password,
          role: 'PATIENT', // or 'DOCTOR' or 'ADMIN' as needed
        });
      }
      setShowForm(false);
      setEditingUser(null);
      setIsEdit(false);
      fetchUsers();
    } catch (error: any) {
      setError(
        error?.response?.data?.error ||
        (error?.response?.data && JSON.stringify(error.response.data)) ||
        'Failed to save user'
      );
      console.error('Failed to save user:', error);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  const formFields = [
    { name: 'username', label: 'Username', type: 'text', required: true },
    { name: 'email', label: 'Email', type: 'email', required: true },
    { name: 'firstName', label: 'First Name', type: 'text', required: true },
    { name: 'lastName', label: 'Last Name', type: 'text', required: true },
    { name: 'isStaff', label: 'Is Staff', type: 'checkbox', required: false },
    { name: 'password', label: 'Password', type: 'password', required: !isEdit },
    { name: 'confirm_password', label: 'Confirm Password', type: 'password', required: !isEdit },
  ];

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Users</h2>
        <button
          onClick={() => {
            setEditingUser(null);
            setShowForm(true);
            setIsEdit(false);
            setError(null);
          }}
          className="px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700"
        >
          Add User
        </button>
      </div>

      {error && <div className="mb-4 text-red-600">{error}</div>}

      {showForm ? (
        <div className="mb-6">
          <EntityForm
            fields={formFields}
            initialData={editingUser ? {
              ...editingUser,
              firstName: editingUser.first_name,
              lastName: editingUser.last_name,
              isStaff: editingUser.is_staff,
              password: '',
              confirm_password: '',
            } : {}}
            onSubmit={handleSubmit}
            onCancel={() => {
              setShowForm(false);
              setEditingUser(null);
              setIsEdit(false);
              setError(null);
            }}
          />
        </div>
      ) : null}

      <Table
        headers={['Username', 'Email', 'First Name', 'Last Name', 'Is Staff']}
        data={users.map(user => ({
          id: user.id,
          username: user.username,
          email: user.email,
          firstname: user.first_name,
          lastname: user.last_name,
          isstaff: user.is_staff
        }))}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
};

export default Users; 