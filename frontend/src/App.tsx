import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProfileSetup from './pages/ProfileSetup';
import AdminPanel from './pages/AdminPanel';
import { useAuth } from './contexts/AuthContext';

const App: React.FC = () => {
  const { user } = useAuth();

  return (
    <Router>
      <Navbar />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route 
          path="/dashboard" 
          element={
            user?.isSuperuser ? (
              <Navigate to="/admin-panel" replace />
            ) : (
              <Dashboard />
            )
          } 
        />
        <Route path="/profile-setup" element={<ProfileSetup />} />
        <Route 
          path="/admin-panel" 
          element={
            user?.isSuperuser ? (
              <AdminPanel />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          } 
        />
        <Route 
          path="/admin/crud" 
          element={
            user?.isSuperuser ? (
              <AdminPanel />
            ) : (
              <Navigate to="/dashboard" replace />
            )
          } 
        />
      </Routes>
    </Router>
  );
};

export default App; 