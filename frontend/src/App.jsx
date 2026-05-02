import { useState } from "react";
import "./App.css";
import AuthPage from "./components/AuthPage.jsx";
import BabySelector from "./components/BabySelector.jsx";
import ChatPanel from "./components/ChatPanel.jsx";
import FeedingGuide from "./components/FeedingGuide.jsx";
import GrowthPanel from "./components/GrowthPanel.jsx";
import LanguageToggle from "./components/LanguageToggle.jsx";
import MilestoneTracker from "./components/MilestoneTracker.jsx";
import VaccineSchedule from "./components/VaccineSchedule.jsx";
import { I18nProvider, useI18n } from "./i18n/index.jsx";
import { AuthProvider, useAuth } from "./state/authStore.jsx";
import { BabyProvider, useBabies } from "./state/babyStore.jsx";

const TABS = [
  { key: "growth", label: "nav.growth" },
  { key: "milestones", label: "nav.milestones" },
  { key: "vaccines", label: "nav.vaccines" },
  { key: "feeding", label: "nav.feeding" },
  { key: "chat", label: "nav.chat" },
];

function MainContent({ tab }) {
  const { activeBaby } = useBabies();
  const { t } = useI18n();

  if (tab === "chat") return <ChatPanel baby={activeBaby} />;

  if (!activeBaby) {
    return (
      <div className="empty-state">
        <p>{t("baby.no_babies")}</p>
      </div>
    );
  }

  switch (tab) {
    case "growth":
      return <GrowthPanel baby={activeBaby} />;
    case "milestones":
      return <MilestoneTracker baby={activeBaby} />;
    case "vaccines":
      return <VaccineSchedule baby={activeBaby} />;
    case "feeding":
      return <FeedingGuide baby={activeBaby} />;
    default:
      return null;
  }
}

function Shell() {
  const { t } = useI18n();
  const { activeBaby } = useBabies();
  const { user, logout } = useAuth();
  const [tab, setTab] = useState("growth");
  const [sidebarOpen, setSidebarOpen] = useState(
    () => window.innerWidth >= 768,
  );
  const isMobile = () => window.innerWidth < 768;
  const closeOnMobile = () => {
    if (isMobile()) setSidebarOpen(false);
  };

  return (
    <div className="app">
      {sidebarOpen && (
        <div
          className="sidebar-overlay"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      <aside className={`sidebar ${sidebarOpen ? "open" : "closed"}`}>
        <div className="sidebar-top">
          <div className="brand">
            <div className="brand-icon">B</div>
            {sidebarOpen && (
              <span className="brand-name">{t("app.title")}</span>
            )}
          </div>
          <button
            className="toggle-btn"
            onClick={() => setSidebarOpen((v) => !v)}
            aria-label="Toggle sidebar"
          >
            {sidebarOpen ? "◀" : "▶"}
          </button>
        </div>

        {sidebarOpen && (
          <>
            <div className="sidebar-section">
              <BabySelector />
            </div>

            <nav className="sidebar-nav">
              <p className="nav-label">Sections</p>
              <ul>
                {TABS.map(({ key, label }) => (
                  <li
                    key={key}
                    className={tab === key ? "active" : ""}
                    onClick={() => {
                      setTab(key);
                      closeOnMobile();
                    }}
                  >
                    {t(label)}
                  </li>
                ))}
              </ul>
            </nav>

            <div className="sidebar-footer">
              <LanguageToggle />
              <p>{t("app.subtitle")}</p>
            </div>
          </>
        )}
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="topbar-left">
            <button
              className="hamburger"
              onClick={() => setSidebarOpen((v) => !v)}
              aria-label="Open menu"
            >
              ☰
            </button>
            <div className="topbar-icon">B</div>
            <div>
              <h1>{t("app.title")}</h1>
              <span className="status">
                <span className="status-dot" />
                {activeBaby
                  ? `${activeBaby.name} · ${t("baby.sex." + activeBaby.sex)}`
                  : t("baby.none_selected")}
              </span>
            </div>
          </div>
          <div className="topbar-tabs">
            {TABS.map(({ key, label }) => (
              <button
                key={key}
                className={`topbar-tab ${tab === key ? "active" : ""}`}
                onClick={() => setTab(key)}
              >
                {t(label)}
              </button>
            ))}
          </div>
          <div className="topbar-right">
            <span className="user-email">{user?.email}</span>
            <button className="logout-btn" onClick={logout}>
              {t("auth.logout")}
            </button>
          </div>
        </header>

        <div className="content-area">
          <MainContent tab={tab} />
        </div>
      </main>
    </div>
  );
}

function AuthGate() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="auth-loading">
        <div className="spinner" />
      </div>
    );
  }

  if (!user) return <AuthPage />;

  return (
    <BabyProvider>
      <Shell />
    </BabyProvider>
  );
}

export default function App() {
  return (
    <I18nProvider>
      <AuthProvider>
        <AuthGate />
      </AuthProvider>
    </I18nProvider>
  );
}
