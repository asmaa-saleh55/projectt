import React from 'react';
import Doctors from '../components/Doctors';
import Patients from '../components/Patients';
import Users from '../components/Users';
import { useAuth } from '../contexts/AuthContext';
import { Navigate } from 'react-router-dom';

const AdminPanel: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = React.useState<'doctors' | 'patients' | 'users'>('doctors');

  // حماية الصفحة: فقط للمخولين (مثلاً: is_staff)
  if (!user || !(user.role === 'ADMIN' || user.role === 'STAFF')) {
    return <Navigate to="/" />;
  }

  const tabs = [
    { id: 'doctors', label: 'Doctors' },
    { id: 'patients', label: 'Patients' },
    { id: 'users', label: 'Users' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <h1 className="text-xl font-bold text-indigo-600">Admin Panel</h1>
              </div>
              <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as 'doctors' | 'patients' | 'users')}
                    className={`$ {
                      activeTab === tab.id
                        ? 'border-indigo-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    {tab.label}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {activeTab === 'doctors' && <Doctors />}
        {activeTab === 'patients' && <Patients />}
        {activeTab === 'users' && <Users />}
      </main>
    </div>
  );
};

export default AdminPanel; 