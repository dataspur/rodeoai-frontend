'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { User, login as apiLogin, getCurrentUser } from './api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Check for stored token on mount
    const storedToken = localStorage.getItem('rodeoai_token');
    if (storedToken) {
      getCurrentUser(storedToken)
        .then(setUser)
        .catch(() => {
          localStorage.removeItem('rodeoai_token');
        })
        .finally(() => setIsLoading(false));
      setToken(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (username: string, password: string) => {
    const { access_token } = await apiLogin(username, password);
    setToken(access_token);
    localStorage.setItem('rodeoai_token', access_token);

    const userData = await getCurrentUser(access_token);
    setUser(userData);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('rodeoai_token');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
