import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { api } from "../api.js";

const STORAGE_KEY = "bha.activeBabyId";
const Context = createContext(null);

export function BabyProvider({ children }) {
  const [babies, setBabies] = useState([]);
  const [activeId, setActiveId] = useState(() => {
    const v = localStorage.getItem(STORAGE_KEY);
    return v ? Number(v) : null;
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    try {
      const list = await api.listBabies();
      setBabies(list);
      setError(null);
      if (activeId && !list.some((b) => b.id === activeId)) {
        setActiveId(list[0]?.id ?? null);
      } else if (!activeId && list.length > 0) {
        setActiveId(list[0].id);
      }
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [activeId]);

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (activeId) localStorage.setItem(STORAGE_KEY, String(activeId));
    else localStorage.removeItem(STORAGE_KEY);
  }, [activeId]);

  const activeBaby = useMemo(
    () => babies.find((b) => b.id === activeId) ?? null,
    [babies, activeId],
  );

  const value = useMemo(
    () => ({
      babies,
      activeBaby,
      activeId,
      setActiveId,
      refresh,
      loading,
      error,
    }),
    [babies, activeBaby, activeId, refresh, loading, error],
  );

  return <Context.Provider value={value}>{children}</Context.Provider>;
}

export function useBabies() {
  const ctx = useContext(Context);
  if (!ctx) throw new Error("useBabies must be used within BabyProvider");
  return ctx;
}
