import { createContext, useContext, useEffect, useMemo, useState } from "react";
import en from "./en.json";
import vi from "./vi.json";

const DICTS = { en, vi };
const STORAGE_KEY = "bha.lang";

const I18nContext = createContext({
  lang: "vi",
  t: (k) => k,
  setLang: () => {},
});

function detectInitial() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved === "en" || saved === "vi") return saved;
  const browser = (navigator.language || "vi").toLowerCase();
  return browser.startsWith("vi") ? "vi" : "en";
}

function format(template, vars) {
  if (!vars) return template;
  return template.replace(/\{(\w+)\}/g, (_, k) =>
    vars[k] === undefined || vars[k] === null ? "" : String(vars[k]),
  );
}

export function I18nProvider({ children }) {
  const [lang, setLangState] = useState(detectInitial);

  useEffect(() => {
    document.documentElement.lang = lang;
    localStorage.setItem(STORAGE_KEY, lang);
  }, [lang]);

  const value = useMemo(
    () => ({
      lang,
      setLang: setLangState,
      t: (key, vars) => {
        const dict = DICTS[lang] || DICTS.en;
        const template = dict[key] ?? DICTS.en[key] ?? key;
        return format(template, vars);
      },
    }),
    [lang],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  return useContext(I18nContext);
}
