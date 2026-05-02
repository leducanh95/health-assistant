import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";

export default function VaccineSchedule({ baby }) {
  const { t, lang } = useI18n();
  const [data, setData] = useState(null);
  const [pendingKey, setPendingKey] = useState(null);
  const [pendingDate, setPendingDate] = useState(
    new Date().toISOString().slice(0, 10),
  );

  const load = async () => {
    setData(await api.vaccinationStatus(baby.id));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baby.id]);

  if (!data) return <div className="panel">…</div>;

  const markReceived = async (item) => {
    await api.addVaccination(baby.id, {
      vaccine_code: item.vaccine_code,
      dose_number: item.dose_number,
      given_at: pendingDate,
    });
    setPendingKey(null);
    load();
  };

  const unmark = async (item) => {
    const list = await api.listVaccinations(baby.id);
    const rec = list.find(
      (r) =>
        r.vaccine_code === item.vaccine_code &&
        r.dose_number === item.dose_number,
    );
    if (rec) {
      await api.deleteVaccination(baby.id, rec.id);
      load();
    }
  };

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>{t("vaccines.title")}</h2>
      </div>
      <ul className="vaccine-list">
        {data.items.map((v, i) => {
          const itemKey = `${v.vaccine_code}-${v.dose_number}-${i}`;
          const label = lang === "vi" ? v.label_vi : v.label_en;
          return (
            <li key={itemKey} className={`vaccine-item status-${v.status}`}>
              <div className="vaccine-row">
                <span
                  className={`vaccine-check ${v.received ? "checked" : ""}`}
                >
                  {v.received ? "✓" : ""}
                </span>
                <div className="vaccine-meta">
                  <span className="vaccine-label">{label}</span>
                  <span className="vaccine-due">
                    {v.received
                      ? t("vaccines.received_on", { date: v.received_at })
                      : t("vaccines.due_date", { date: v.due_date })}
                  </span>
                </div>
                <span className={`status-pill status-${v.status}`}>
                  {t(`vaccines.${v.status}`)}
                </span>
              </div>
              {v.received ? (
                <button className="link" onClick={() => unmark(v)}>
                  {t("milestones.unmark")}
                </button>
              ) : pendingKey === itemKey ? (
                <div className="inline-form">
                  <input
                    type="date"
                    value={pendingDate}
                    onChange={(e) => setPendingDate(e.target.value)}
                  />
                  <button
                    className="primary"
                    onClick={() => markReceived(v)}
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
                  onClick={() => setPendingKey(itemKey)}
                >
                  {t("vaccines.mark_received")}
                </button>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}
