import api from './config';

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData extends LoginCredentials {
  firstName: string;
  lastName: string;
  role: 'patient' | 'doctor';
  specialization?: string;
  experienceYears?: number;
  qualification?: string;
  consultationFee?: number;
  availableDays?: string[];
  availableTimes?: string[];
}

interface AuthResponse {
  token: string;
  user: {
    id: string;
    email: string;
    firstName: string;
    lastName: string;
    role: string;
    isSuperuser?: boolean;
    isStaff?: boolean;
  };
}

export const authService = {
  async login(credentials: LoginCredentials): Promise<AuthResponse> {
    try {
      console.log('Attempting login with:', credentials.email);
      const response = await api.post('/api/token/', {
        email: credentials.email,
        password: credentials.password
      });
      console.log('Token response:', response.data);

      if (response.data.access) {
        localStorage.setItem('token', response.data.access);
        localStorage.setItem('refresh_token', response.data.refresh);
        api.defaults.headers.common['Authorization'] = `Bearer ${response.data.access}`;
        
        console.log('Fetching user profile...');
        const userResponse = await api.get('/api/users/me/');
        console.log('User profile response:', userResponse.data);
        
        let userData = userResponse.data;
        
        const transformedUser = {
          id: userData.id,
          email: userData.email,
          firstName: userData.first_name,
          lastName: userData.last_name,
          role: userData.is_superuser ? 'ADMIN' : userData.role,
          isSuperuser: userData.is_superuser,
          isStaff: userData.is_staff
        };
        console.log('Transformed user data:', transformedUser);

        localStorage.setItem('user', JSON.stringify(transformedUser));
        return {
          token: response.data.access,
          user: transformedUser
        };
      }
      throw new Error('No access token in response');
    } catch (error: any) {
      console.error('Login error details:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message
      });
      throw error;
    }
  },

  async register(data: RegisterData): Promise<AuthResponse> {
    const backendData = {
      first_name: data.firstName,
      last_name: data.lastName,
      email: data.email,
      password: data.password,
      role: data.role.toUpperCase(),
      specialization: data.specialization,
      experience_years: data.experienceYears,
      qualification: data.qualification,
      consultation_fee: data.consultationFee,
      available_days: data.availableDays,
      available_times: data.availableTimes
    };

    const response = await api.post('/api/register/', backendData);
    if (response.data.tokens.access) {
      const transformedUser = {
        id: response.data.user.id,
        email: response.data.user.email,
        firstName: response.data.user.first_name,
        lastName: response.data.user.last_name,
        role: response.data.user.role,
        isSuperuser: response.data.user.is_superuser,
        isStaff: response.data.user.is_staff
      };

      localStorage.setItem('token', response.data.tokens.access);
      localStorage.setItem('refresh_token', response.data.tokens.refresh);
      localStorage.setItem('user', JSON.stringify(transformedUser));
      
      return {
        token: response.data.tokens.access,
        user: transformedUser
      };
    }
    throw new Error('Registration failed');
  },

  logout(): void {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    delete api.defaults.headers.common['Authorization'];
  },

  getCurrentUser(): any {
    const userStr = localStorage.getItem('user');
    if (userStr) return JSON.parse(userStr);
    return null;
  },

  getToken(): string | null {
    return localStorage.getItem('token');
  }
}; 