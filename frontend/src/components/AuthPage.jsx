import { useState } from "react";
import { useI18n } from "../i18n/index.jsx";
import { useAuth } from "../state/authStore.jsx";

export default function AuthPage() {
  const { t } = useI18n();
  const { login, signup } = useAuth();
  const [mode, setMode] = useState("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await signup(email, password);
      }
    } catch (err) {
      const msg = err.message || "";
      if (msg.includes("409")) {
        setError(t("auth.error.email_taken"));
      } else if (msg.includes("401")) {
        setError(t("auth.error.invalid_credentials"));
      } else if (password.length < 8) {
        setError(t("auth.error.weak_password"));
      } else {
        setError(msg);
      }
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="brand auth-brand">
          <div className="brand-icon">B</div>
          <span className="brand-name">{t("app.title")}</span>
        </div>
        <h2>
          {mode === "login" ? t("auth.login.title") : t("auth.signup.title")}
        </h2>

        {error && <p className="auth-error">{error}</p>}

        <form onSubmit={submit}>
          <label>
            {t("auth.email")}
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
          </label>
          <label>
            {t("auth.password")}
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete={
                mode === "login" ? "current-password" : "new-password"
              }
            />
          </label>
          {mode === "signup" && (
            <p className="auth-hint">{t("auth.password_min")}</p>
          )}
          <button type="submit" className="primary auth-submit" disabled={busy}>
            {mode === "login"
              ? t("auth.submit_login")
              : t("auth.submit_signup")}
          </button>
        </form>

        <p className="auth-switch">
          {mode === "login" ? (
            <>
              {t("auth.switch_to_signup")}{" "}
              <button
                className="link-btn"
                onClick={() => {
                  setMode("signup");
                  setError("");
                }}
              >
                {t("auth.signup.title")}
              </button>
            </>
          ) : (
            <>
              {t("auth.switch_to_login")}{" "}
              <button
                className="link-btn"
                onClick={() => {
                  setMode("login");
                  setError("");
                }}
              >
                {t("auth.login.title")}
              </button>
            </>
          )}
        </p>
      </div>
    </div>
  );
}
