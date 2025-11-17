import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import logger from '@/utils/logger';

const BACKEND_URL = "https://8000-iawczpd16uqen9op7vv32-370d3fde.manusvm.computer";

interface User {
  id: number;
  email: string;
  name: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: () => void;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = async () => {
    try {
      const response = await fetch(`${BACKEND_URL}/api/auth/status/`, {
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.authenticated && data.user) {
          setUser(data.user);
        } else {
          setUser(null);
        }
      } else {
        setUser(null);
      }
    } catch (error) {
      logger.error('Auth check failed', error);
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const login = () => {
    window.location.href = `${BACKEND_URL}/accounts/google/login/`;
  };

  const logout = async () => {
    try {
      await fetch(`${BACKEND_URL}/api/auth/logout/`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      logger.error('Logout failed', error);
    }
    setUser(null);
    window.location.href = '/login';
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, checkAuth }}>
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

