"use client";

import { useState, useEffect, createContext, useContext, ReactNode } from "react";
import { User, UserRole } from "../lib/types";
import { DEMO_USERS, tokenManager } from "../lib/api";
import { useRouter } from "next/navigation";

interface AuthContextType {
  user: User | null;
  role: UserRole;
  setRole: (role: UserRole) => void;
  loginAs: (role: UserRole) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType>({
  user: DEMO_USERS.tpo,
  role: "tpo",
  setRole: () => {},
  loginAs: () => {},
  logout: () => {},
  isAuthenticated: true,
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(DEMO_USERS.tpo);
  const [role, setRoleState] = useState<UserRole>("tpo");
  const router = useRouter();

  useEffect(() => {
    // Check saved session
    const savedUser = tokenManager.getCurrentUser();
    if (savedUser) {
      setUser(savedUser);
      setRoleState(savedUser.role);
    } else {
      // Default to TPO for demo showcases
      setUser(DEMO_USERS.tpo);
      setRoleState("tpo");
      tokenManager.setAuth({
        access_token: "mock-default-token",
        user: DEMO_USERS.tpo,
      });
    }
  }, []);

  const loginAs = (newRole: UserRole) => {
    const targetUser = DEMO_USERS[newRole];
    setUser(targetUser);
    setRoleState(newRole);
    tokenManager.setAuth({
      access_token: `mock-token-${newRole}`,
      user: targetUser,
    });
    router.push(`/${newRole}`);
  };

  const setRole = (newRole: UserRole) => {
    loginAs(newRole);
  };

  const logout = () => {
    tokenManager.clearAuth();
    setUser(null);
    router.push("/login");
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        role,
        setRole,
        loginAs,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
