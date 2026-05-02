import { useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";
import { useBabies } from "../state/babyStore.jsx";

function ageMonths(birthDateIso) {
  if (!birthDateIso) return 0;
  const dob = new Date(birthDateIso);
  const now = new Date();
  return Math.max(0, (now - dob) / (1000 * 60 * 60 * 24 * 30.4375));
}

function BabyForm({ initial, onSave, onCancel }) {
  const { t } = useI18n();
  const [name, setName] = useState(initial?.name ?? "");
  const [sex, setSex] = useState(initial?.sex ?? "M");
  const [birthDate, setBirthDate] = useState(
    initial?.birth_date ?? new Date().toISOString().slice(0, 10),
  );
  const [notes, setNotes] = useState(initial?.notes ?? "");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!name.trim() || !birthDate) return;
    setBusy(true);
    try {
      await onSave({ name: name.trim(), sex, birth_date: birthDate, notes });
    } finally {
      setBusy(false);
    }
  };

  return (
    <form className="baby-form" onSubmit={submit}>
      <label>
        {t("baby.name")}
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
          maxLength={120}
        />
      </label>
      <label>
        {t("baby.sex")}
        <select value={sex} onChange={(e) => setSex(e.target.value)}>
          <option value="M">{t("baby.sex.M")}</option>
          <option value="F">{t("baby.sex.F")}</option>
        </select>
      </label>
      <label>
        {t("baby.birth_date")}
        <input
          type="date"
          value={birthDate}
          onChange={(e) => setBirthDate(e.target.value)}
          required
        />
      </label>
      <label>
        {t("baby.notes")}
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
        />
      </label>
      <div className="form-actions">
        <button type="button" onClick={onCancel} disabled={busy}>
          {t("baby.cancel")}
        </button>
        <button type="submit" className="primary" disabled={busy}>
          {t("baby.save")}
        </button>
      </div>
    </form>
  );
}

export default function BabySelector() {
  const { babies, activeId, setActiveId, refresh } = useBabies();
  const { t } = useI18n();
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);

  const onCreate = async (data) => {
    const baby = await api.createBaby(data);
    setActiveId(baby.id);
    setShowForm(false);
    refresh();
  };

  const onUpdate = async (data) => {
    await api.updateBaby(editing.id, data);
    setEditing(null);
    refresh();
  };

  return (
    <div className="baby-selector">
      <p className="nav-label">Babies</p>

      {babies.length === 0 && !showForm && (
        <p className="muted">{t("baby.no_babies")}</p>
      )}

      <ul className="baby-list">
        {babies.map((b) => (
          <li
            key={b.id}
            className={`baby-item ${b.id === activeId ? "active" : ""}`}
          >
            <button
              className="baby-row"
              onClick={() => setActiveId(b.id)}
              title={`${b.name} (${b.sex})`}
            >
              <span className="baby-avatar">
                {b.name.slice(0, 1).toUpperCase()}
              </span>
              <span className="baby-meta">
                <span className="baby-name">{b.name}</span>
                <span className="baby-age">
                  {t("baby.age_months", {
                    months: ageMonths(b.birth_date).toFixed(1),
                  })}
                </span>
              </span>
            </button>
            <div className="baby-actions">
              <button onClick={() => setEditing(b)} title={t("baby.edit")}>
                ✎
              </button>
            </div>
          </li>
        ))}
      </ul>

      {!showForm && !editing && (
        <button
          className="add-baby-btn"
          onClick={() => setShowForm(true)}
        >
          {t("baby.add")}
        </button>
      )}

      {showForm && (
        <BabyForm onSave={onCreate} onCancel={() => setShowForm(false)} />
      )}
      {editing && (
        <BabyForm
          initial={editing}
          onSave={onUpdate}
          onCancel={() => setEditing(null)}
        />
      )}
    </div>
  );
}
