import { createContext, FC, ReactNode, useContext, useEffect, useState } from "react";

interface AuthContextType {
  isAuthenticated: boolean;
  name: string | null;
  login: (token: string) => void;
  logout: () => void;
}

interface AuthProviderProps {
  children: ReactNode;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: FC<AuthProviderProps> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(!!localStorage.getItem("token"));
  const [name, setName] = useState<string | null>(null);

  const login = (accessToken: string) => {
    localStorage.setItem("access", accessToken);
    setIsAuthenticated(true);
    // fetchUserDetails();
  };

  const logout = () => {
    localStorage.removeItem("access");
    setIsAuthenticated(false);
    setName(null);
  };

  const fetchUserDetails = async () => {
    const token = localStorage.getItem("access");
    if (!token) {
      logout();
      return;
    }

    try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/users/me/`, {
            headers: { Authorization: `Bearer ${localStorage.getItem("access")}` },
          });
  
        if (!response.ok) throw new Error("Failed to fetch user details.");
  
        const data = await response.json();
        setName(data.first_name || "Guest");
        setIsAuthenticated(true); 
    } catch (error) {
        console.error("Error fetching user details:", error);
        logout();
    }
  };

  useEffect(() => {
    fetchUserDetails();
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, name, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
