import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const user = { username: 'Test User', role: 'Patient' }; // Temporary mock data

  const handleLogout = () => {
    // TODO: Implement actual logout logic
    console.log('Logout');
    navigate('/login');
  };

  const renderRoleSpecificContent = () => {
    switch (user?.role) {
      case 'Admin':
        return (
          <button
            onClick={() => navigate('/admin')}
            className="mt-4 bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded"
          >
            Go to Admin Dashboard
          </button>
        );
      case 'Doctor':
        return (
          <button
            onClick={() => navigate('/patients')}
            className="mt-4 bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
          >
            My Patients
          </button>
        );
      case 'Patient':
        return (
          <button
            onClick={() => navigate('/prescriptions')}
            className="mt-4 bg-purple-500 hover:bg-purple-600 text-white font-bold py-2 px-4 rounded"
          >
            My Prescriptions
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div className="relative py-3 sm:max-w-xl sm:mx-auto">
        <div className="relative px-4 py-10 bg-white mx-8 md:mx-0 shadow rounded-3xl sm:p-10">
          <div className="max-w-md mx-auto">
            <div className="divide-y divide-gray-200">
              <div className="py-8 text-base leading-6 space-y-4 text-gray-700 sm:text-lg sm:leading-7">
                <h1 className="text-2xl font-bold text-center mb-4">
                  Welcome, {user?.username}!
                </h1>
                <p className="text-center mb-4">
                  You are logged in as {user?.role}
                </p>
                {renderRoleSpecificContent()}
                <button
                  onClick={handleLogout}
                  className="mt-4 w-full bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Home; 