import React, { createContext, useContext, useState, useEffect } from "react";
import { useQueryClient, useMutation } from "@tanstack/react-query";

const UserAuthContext = createContext();

export function UserAuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const queryClient = useQueryClient();

  // Check for existing token on initial load
  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setUser({ token });
    }
  }, []);

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async ({ email, password }) => {
      const response = await fetch("http://127.0.0.1:8000/api/users/login/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username: email, password }), // Backend expects username
      });
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Login failed");
      }
      return response.json();
    },
    onSuccess: (data) => {
      localStorage.setItem("token", data.access); // Use access token
      setUser({ token: data.access, email: data.user.email });
      queryClient.invalidateQueries(["user"]);
    },
    onError: (error) => {
      console.error("Login error:", error.message);
    },
  });

  // Register patient mutation
  const registerPatientMutation = useMutation({
    mutationFn: async ({ fullName, email, password }) => {
      // Debug input values
      console.log('Registration inputs:', {
        fullName,
        email,
        password: password ? '****' : 'undefined'
      });

      // Validate required fields
      if (!fullName || !email || !password) {
        throw new Error('Full name, email, and password are required');
      }

      // Validate password specifically
      if (typeof password !== 'string') {
        throw new Error('Password must be a string');
      }

      const trimmedPassword = password.trim();
      if (trimmedPassword.length === 0) {
        throw new Error('Password cannot be empty or just whitespace');
      }

      const parts = fullName.trim().split(" ");
      const first_name = parts[0];
      const last_name = parts.length > 1 ? parts.slice(1).join(" ") : "N/A";

      // Create base request data with required fields
      const requestData = {
        first_name,
        last_name,
        email: email.trim(),
        password: trimmedPassword // Use the validated and trimmed password
      };

      // Clean up and add optional fields only if they have valid values
      const optionalFields = {
        age: null,
        gender: "",
        date_of_birth: "",
        blood_group: "",
        medical_history: ""
      };

      // Only add non-empty fields to the request
      Object.entries(optionalFields).forEach(([key, value]) => {
        if (value !== null && value !== "" && value !== undefined) {
          // Special handling for age - only include if it's a valid number
          if (key === 'age' && !isNaN(value) && value !== "") {
            requestData[key] = parseInt(value, 10);
          }
          // Special handling for date_of_birth - only include if it's a valid date string
          else if (key === 'date_of_birth' && value && value.match(/^\d{4}-\d{2}-\d{2}$/)) {
            requestData[key] = value;
          }
          // For other fields, only include if they're not empty strings
          else if (key !== 'age' && key !== 'date_of_birth' && value !== "") {
            requestData[key] = value;
          }
        }
      });

      // Debug the final request data (with masked password)
      console.log('Final request data (masked):', {
        ...requestData,
        password: '****'
      });

      // Debug the actual request data with raw password
      console.log('DEBUG - Raw request data:', requestData);

      try {
        // Log the exact object being stringified
        console.log('DEBUG - Object being stringified:', JSON.stringify(requestData, null, 2));

        const response = await fetch("http://127.0.0.1:8000/api/register/patient/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/json"
          },
          body: JSON.stringify(requestData),
        });

        const responseData = await response.json();
        console.log('Registration response:', responseData);

        if (!response.ok) {
          const errorMessage = responseData.details 
            ? (Array.isArray(responseData.details) 
                ? responseData.details.join(', ') 
                : responseData.details)
            : responseData.error || "Registration failed";
          throw new Error(errorMessage);
        }
        return responseData;
      } catch (error) {
        console.error('Registration request failed:', error);
        throw error;
      }
    },
    onSuccess: (data) => {
      localStorage.setItem("token", data.tokens.access);
      setUser({ token: data.tokens.access, email: data.user.user.email });
      queryClient.invalidateQueries(["user"]);
    },
    onError: (error) => {
      console.error("Patient registration error:", error.message);
    },
  });

  // Register doctor mutation
  const registerDoctorMutation = useMutation({
    mutationFn: async ({ fullName, email, password, license }) => {
      // Validate password
      if (!password || typeof password !== 'string' || password.trim() === '') {
        throw new Error('Password is required and cannot be empty');
      }

      console.log('Password validation passed:', password ? 'Password provided' : 'No password');

      const parts = fullName.trim().split(" ");
      const first_name = parts[0];
      const last_name = parts.length > 1 ? parts.slice(1).join(" ") : "N/A";

      const formData = new FormData();
      formData.append('first_name', first_name);
      formData.append('last_name', last_name);
      formData.append('email', email);
      formData.append('password', password.trim()); // Ensure password is trimmed
      formData.append('medical_license', license);
      formData.append('specialty', 'General Medicine');
      formData.append('working_hours', '9am-5pm');
      formData.append('certificates', '');
      formData.append('experience_years', '0');
      formData.append('qualification', 'MBBS');
      formData.append('consultation_fee', '0');
      formData.append('available_days', JSON.stringify(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']));
      formData.append('available_times', JSON.stringify(['09:00', '10:00', '11:00', '14:00', '15:00']));

      // Log form data without password
      const formDataObj = Object.fromEntries(formData);
      console.log('Sending doctor registration data:', { ...formDataObj, password: '***' });

      const response = await fetch("http://127.0.0.1:8000/api/register/doctor/", {
        method: "POST",
        headers: {
          "Accept": "application/json"
        },
        body: formData,
      });

      const responseData = await response.json();
      console.log('Doctor registration response:', responseData);

      if (!response.ok) {
        const errorMessage = responseData.details 
          ? (Array.isArray(responseData.details) 
              ? responseData.details.join(', ') 
              : responseData.details)
          : responseData.error || "Registration failed";
        throw new Error(errorMessage);
      }
      return responseData;
    },
    onSuccess: (data) => {
      localStorage.setItem("token", data.tokens.access);
      setUser({ token: data.tokens.access, email: data.user.user.email });
      queryClient.invalidateQueries(["user"]);
    },
    onError: (error) => {
      console.error("Doctor registration error:", error.message);
    },
  });

  const logout = () => {
    localStorage.removeItem("token");
    setUser(null);
    queryClient.clear();
  };

  return (
    <UserAuthContext.Provider
      value={{
        user,
        login: loginMutation,
        registerPatient: registerPatientMutation,
        registerDoctor: registerDoctorMutation,
        logout,
      }}
    >
      {children}
    </UserAuthContext.Provider>
  );
}

export const useUserAuth = () => {
  const context = useContext(UserAuthContext);
  if (!context) {
    throw new Error("useUserAuth must be used within a UserAuthProvider");
  }
  return context;
};