import { createContext, useContext, useEffect, useState } from "react";
import { loginUser, registerUser } from "../api";

const AuthContext = createContext(null);

// Decodes the payload of a JWT without any extra dependency.
// This only reads the token locally; it does not verify the signature
// (verification happens server-side on every request).
function decodeUser(token) {
  try {
    const base64Url = token.split(".")[1];
    const base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
    const payload = JSON.parse(decodeURIComponent(escape(window.atob(base64))));
    return { email: payload.sub, role: payload.role };
  } catch {
    return null;
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem("token") || "");
  const [user, setUser] = useState(() => {
    const stored = localStorage.getItem("token");
    return stored ? decodeUser(stored) : null;
  });

  useEffect(() => {
    if (token) {
      localStorage.setItem("token", token);
      setUser(decodeUser(token));
    } else {
      localStorage.removeItem("token");
      setUser(null);
    }
  }, [token]);

  const login = async (email, password) => {
    const res = await loginUser({ email, password });
    setToken(res.data.access_token);
  };

  const register = async (email, password, role) => {
    await registerUser({ email, password, role });
  };

  const logout = () => setToken("");

  return (
    <AuthContext.Provider value={{ token, user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
