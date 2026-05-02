import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";

export default function MilestoneTracker({ baby }) {
  const { t, lang } = useI18n();
  const [data, setData] = useState(null);
  const [pendingKey, setPendingKey] = useState(null);
  const [pendingDate, setPendingDate] = useState(
    new Date().toISOString().slice(0, 10),
  );

  const load = async () => {
    setData(await api.milestoneStatus(baby.id));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baby.id]);

  if (!data) return <div className="panel">…</div>;

  const markAchieved = async (key) => {
    await api.upsertMilestone(baby.id, {
      milestone_key: key,
      achieved_at: pendingDate,
    });
    setPendingKey(null);
    load();
  };

  const unmark = async (key) => {
    const records = await api.listMilestoneRecords(baby.id);
    const r = records.find((x) => x.milestone_key === key);
    if (r) {
      await api.deleteMilestone(baby.id, r.id);
      load();
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>{t("milestones.title")}</h2>
      </div>
      <ul className="milestone-list">
        {data.items.map((m) => {
          const label = lang === "vi" ? m.label_vi : m.label_en;
          const desc = lang === "vi" ? m.description_vi : m.description_en;
          return (
            <li key={m.key} className={`milestone-item status-${m.status}`}>
              <div className="milestone-head">
                <span
                  className={`milestone-check ${m.achieved ? "checked" : ""}`}
                >
                  {m.achieved ? "✓" : ""}
                </span>
                <div className="milestone-meta">
                  <span className="milestone-label">{label}</span>
                  <span className="milestone-window">
                    {t("milestones.window", {
                      p1: m.p1_months,
                      p99: m.p99_months,
                      median: m.median_months,
                    })}
                  </span>
                </div>
                <span className={`status-pill status-${m.status}`}>
                  {t(`milestones.${m.status}`)}
                </span>
              </div>
              <p className="milestone-desc">{desc}</p>
              {m.achieved && (
                <p className="milestone-achieved">
                  {t("milestones.achieved_at", {
                    age: m.achieved_age_months,
                  })}{" "}
                  ·{" "}
                  <button className="link" onClick={() => unmark(m.key)}>
                    {t("milestones.unmark")}
                  </button>
                </p>
              )}
              {!m.achieved &&
                (pendingKey === m.key ? (
                  <div className="inline-form milestone-form">
                    <input
                      type="date"
                      value={pendingDate}
                      onChange={(e) => setPendingDate(e.target.value)}
                    />
                    <button
                      className="primary"
                      onClick={() => markAchieved(m.key)}
                    >
                      {t("baby.save")}
                    </button>
                    <button onClick={() => setPendingKey(null)}>
                      {t("baby.cancel")}
                    </button>
                  </div>
                ) : (
                  <button
                    className="link"
                    onClick={() => setPendingKey(m.key)}
                  >
                    {t("milestones.mark_done")}
                  </button>
                ))}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
