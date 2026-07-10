import React, { createContext, useContext, useState, useEffect } from 'react';
import { api, getAuthToken, setAuthToken, clearAuthToken } from '../services/api';

interface User {
  id: number;
  username: string;
  email: string;
  balance: number;
  security_score: number;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (data: any) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchUser = async () => {
    try {
      const userData = await api.auth.me();
      setUser(userData);
    } catch (err) {
      console.error('Failed to load session user profile', err);
      clearAuthToken();
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = getAuthToken();
    if (token) {
      fetchUser();
    } else {
      setLoading(false);
    }
  }, []);

  const login = async (data: any) => {
    setLoading(true);
    try {
      const response = await api.auth.login(data);
      setAuthToken(response.access_token);
      await fetchUser();
    } catch (err) {
      setLoading(false);
      throw err;
    }
  };

  const register = async (data: any) => {
    setLoading(true);
    try {
      const response = await api.auth.register(data);
      setAuthToken(response.access_token);
      await fetchUser();
    } catch (err) {
      setLoading(false);
      throw err;
    }
  };

  const logout = () => {
    clearAuthToken();
    setUser(null);
  };

  const refreshUser = async () => {
    try {
      const userData = await api.auth.me();
      setUser(userData);
    } catch (err) {
      console.error('Failed to refresh user profile data', err);
    }
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
