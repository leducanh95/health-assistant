import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api } from "../api.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem("bha.token");
    if (!token) {
      setLoading(false);
      return;
    }
    api
      .me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("bha.token");
      })
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const onExpired = () => setUser(null);
    window.addEventListener("bha:auth-expired", onExpired);
    return () => window.removeEventListener("bha:auth-expired", onExpired);
  }, []);

  const login = useCallback(async (email, password) => {
    const { access_token } = await api.login(email, password);
    localStorage.setItem("bha.token", access_token);
    const me = await api.me();
    setUser(me);
  }, []);

  const signup = useCallback(async (email, password) => {
    const { access_token } = await api.signup(email, password);
    localStorage.setItem("bha.token", access_token);
    const me = await api.me();
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("bha.token");
    localStorage.removeItem("bha.activeBabyId");
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({ user, loading, login, signup, logout }),
    [user, loading, login, signup, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
