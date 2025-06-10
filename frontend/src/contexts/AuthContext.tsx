import React, { createContext, useContext, useState, useEffect } from 'react';
import { authService } from '../api/auth';
import api from '../api/config';

interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: string;
  isSuperuser?: boolean;
  isStaff?: boolean;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<User>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const initializeAuth = async () => {
      const token = localStorage.getItem('token');
      const storedUser = localStorage.getItem('user');

      if (token && storedUser) {
        api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
        try {
          const response = await api.get('/api/users/me/');
          const userData = {
            id: Number(response.data.id),
            email: response.data.email,
            firstName: response.data.first_name,
            lastName: response.data.last_name,
            role: response.data.is_superuser ? 'ADMIN' : response.data.role,
            isSuperuser: response.data.is_superuser,
            isStaff: response.data.is_staff
          };
          setUser(userData);
          setIsAuthenticated(true);
        } catch (error) {
          localStorage.removeItem('token');
          localStorage.removeItem('refresh_token');
          localStorage.removeItem('user');
          delete api.defaults.headers.common['Authorization'];
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string): Promise<User> => {
    try {
      const response = await authService.login({ email, password });
      const userData = {
        ...response.user,
        id: Number(response.user.id)
      };
      
      setUser(userData);
      setIsAuthenticated(true);
      return userData;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  };

  const logout = () => {
    authService.logout();
    setUser(null);
  };

  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated,
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">
      <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
    </div>;
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 