import { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { useLocation } from "wouter";

const API_BASE = ((import.meta as any).env?.VITE_API_URL as string) ?? "";

interface AuthContextType {
  doctorName: string | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
  isAuthenticated: boolean;
  error: string | null;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [doctorName, setDoctorName] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [, setLocation] = useLocation();

  useEffect(() => {
    const token = localStorage.getItem("token");
    const name = localStorage.getItem("doctorName");
    if (token && name) {
      setDoctorName(name);
    } else {
      // Clear incomplete storage sessions (but don't redirect on initial load)
      localStorage.removeItem("token");
      localStorage.removeItem("doctorName");
    }
  }, []);

  // Aligned with POST /auth/login scenario 4
  const login = async (email: string, password: string) => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || body.message || `Error ${res.status}`);
      }

      const data = await res.json();
      
      // Extract values matching your backend response layout
      localStorage.setItem("token", data.access_token);
      
      // Fallback name parsing if UserOut profile data isn't joined on the endpoint response
      const profileName = data.full_name || email.split("@")[0];
      localStorage.setItem("doctorName", profileName);
      
      setDoctorName(profileName);
      setLocation("/dashboard");
    } catch (err: any) {
      setError(err.message || "Invalid credentials");
      throw err;
    }
  };

  // Aligned with POST /auth/register scenario 1
  const signup = async (name: string, email: string, password: string) => {
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          full_name: name,
        }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.detail || body.message || `Registration Failed`);
      }

      // Automatically redirect them to log in smoothly following registration
      await login(email, password);
    } catch (err: any) {
      setError(err.message || "Registration failed");
      throw err;
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("doctorName");
    setDoctorName(null);
    setError(null);
    setLocation("/login");
  };

  const clearError = () => {
    setError(null);
  };

  return (
    <AuthContext.Provider value={{ doctorName, login, signup, logout, clearError, isAuthenticated: !!doctorName, error }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
