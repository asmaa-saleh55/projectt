import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navbar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();

  const isAdmin = user && (user.role === 'ADMIN' || user.role === 'STAFF');

  return (
    <nav className="bg-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-gray-800">
              Task Manager
            </Link>
          </div>
          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/dashboard" className="text-gray-600 hover:text-gray-800">
                  Dashboard
                </Link>
                {isAdmin && (
                  <Link to="/admin-panel" className="text-indigo-600 hover:underline">
                    Admin Panel
                  </Link>
                )}
                <button
                  onClick={logout}
                  className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link to="/login" className="text-gray-600 hover:text-gray-800">
                  Login
                </Link>
                <Link
                  to="/register"
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                >
                  Register
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar; 