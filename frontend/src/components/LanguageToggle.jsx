import { useI18n } from "../i18n/index.jsx";

export default function LanguageToggle() {
  const { lang, setLang, t } = useI18n();
  return (
    <button
      className="lang-toggle"
      onClick={() => setLang(lang === "vi" ? "en" : "vi")}
      title={t("language.toggle")}
    >
      {t("language.toggle")}
    </button>
  );
}
