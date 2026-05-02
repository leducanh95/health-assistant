import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";
import GrowthChart from "./GrowthChart.jsx";
import GrowthReferenceTable from "./GrowthReferenceTable.jsx";

const INDICATORS = [
  "weight_for_age",
  "length_for_age",
  "head_circumference_for_age",
];

function StatusPill({ status }) {
  const { t } = useI18n();
  return (
    <span className={`status-pill status-${status}`}>
      {t(`growth.status.${status}`)}
    </span>
  );
}

function MeasurementForm({ babyId, onSaved }) {
  const { t } = useI18n();
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [weight, setWeight] = useState("");
  const [length, setLength] = useState("");
  const [head, setHead] = useState("");
  const [busy, setBusy] = useState(false);
  const [open, setOpen] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      await api.addMeasurement(babyId, {
        measured_at: date,
        weight_kg: weight ? Number(weight) : null,
        length_cm: length ? Number(length) : null,
        head_circ_cm: head ? Number(head) : null,
      });
      setWeight("");
      setLength("");
      setHead("");
      setOpen(false);
      onSaved?.();
    } finally {
      setBusy(false);
    }
  };

  if (!open) {
    return (
      <button className="primary" onClick={() => setOpen(true)}>
        {t("growth.add")}
      </button>
    );
  }

  return (
    <form className="inline-form" onSubmit={submit}>
      <label>
        {t("growth.measurement_date")}
        <input
          type="date"
          value={date}
          onChange={(e) => setDate(e.target.value)}
          required
        />
      </label>
      <label>
        {t("growth.weight")}
        <input
          type="number"
          min="0"
          step="0.01"
          value={weight}
          onChange={(e) => setWeight(e.target.value)}
        />
      </label>
      <label>
        {t("growth.length")}
        <input
          type="number"
          min="0"
          step="0.1"
          value={length}
          onChange={(e) => setLength(e.target.value)}
        />
      </label>
      <label>
        {t("growth.head")}
        <input
          type="number"
          min="0"
          step="0.1"
          value={head}
          onChange={(e) => setHead(e.target.value)}
        />
      </label>
      <div className="form-actions">
        <button type="button" onClick={() => setOpen(false)} disabled={busy}>
          {t("baby.cancel")}
        </button>
        <button type="submit" className="primary" disabled={busy}>
          {t("baby.save")}
        </button>
      </div>
    </form>
  );
}

export default function GrowthPanel({ baby }) {
  const { t } = useI18n();
  const [status, setStatus] = useState(null);
  const [tab, setTab] = useState("weight_for_age");

  const load = async () => {
    setStatus(await api.growthStatus(baby.id));
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [baby.id]);

  if (!status) return <div className="panel">…</div>;

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>{t("growth.title")}</h2>
        <MeasurementForm babyId={baby.id} onSaved={load} />
      </div>

      {status.assessments.length > 0 && (
        <div className="assessment-cards">
          {status.assessments.map((a) => (
            <div key={a.indicator} className="assessment-card">
              <span className="card-label">
                {t(`growth.indicator.${a.indicator}`)}
              </span>
              <span className="card-value">{a.value}</span>
              <span className="card-pct">P{a.percentile.toFixed(0)}</span>
              <StatusPill status={a.status} />
            </div>
          ))}
        </div>
      )}

      {status.history.length === 0 ? (
        <p className="muted">{t("growth.no_data")}</p>
      ) : (
        <>
          <div className="tabs">
            {INDICATORS.map((ind) => (
              <button
                key={ind}
                className={`tab ${tab === ind ? "active" : ""}`}
                onClick={() => setTab(ind)}
              >
                {t(`growth.indicator.${ind}`)}
              </button>
            ))}
          </div>
          <GrowthChart
            baby={baby}
            indicator={tab}
            history={status.history}
          />
          <GrowthReferenceTable sex={baby.sex} />
        </>
      )}
    </div>
  );
}
