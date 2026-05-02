import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";

function ageMonths(birthDate) {
  if (!birthDate) return 0;
  const dob = new Date(birthDate);
  const now = new Date();
  return Math.max(0, (now - dob) / (1000 * 60 * 60 * 24 * 30.4375));
}

function NutritionCard({ stage, t, lang }) {
  const n = stage.daily_nutrition;
  const note = lang === "vi" ? n.calories_note_vi : n.calories_note_en;

  const nutrients = [
    { key: "protein", label: t("feeding.nutrition.protein"), value: n.protein_g, unit: t("feeding.nutrition.unit_g") },
    { key: "iron", label: t("feeding.nutrition.iron"), value: n.iron_mg, unit: t("feeding.nutrition.unit_mg") },
    { key: "calcium", label: t("feeding.nutrition.calcium"), value: n.calcium_mg, unit: t("feeding.nutrition.unit_mg") },
    { key: "zinc", label: t("feeding.nutrition.zinc"), value: n.zinc_mg, unit: t("feeding.nutrition.unit_mg") },
    { key: "vitamin_a", label: t("feeding.nutrition.vitamin_a"), value: n.vitamin_a_mcg, unit: t("feeding.nutrition.unit_mcg") },
    { key: "vitamin_c", label: t("feeding.nutrition.vitamin_c"), value: n.vitamin_c_mg, unit: t("feeding.nutrition.unit_mg") },
    { key: "vitamin_d", label: t("feeding.nutrition.vitamin_d"), value: n.vitamin_d_mcg, unit: t("feeding.nutrition.unit_mcg") },
  ];

  return (
    <div className="nutrition-card">
      <h3 className="nutrition-card-title">{t("feeding.nutrition.title")}</h3>
      <div className="calories-block">
        <span className="calories-value">{n.calories_kcal}</span>
        <span className="calories-unit">{t("feeding.nutrition.unit_kcal")}</span>
        <p className="calories-note">{note}</p>
      </div>
      <div className="nutrients-grid">
        {nutrients.map((nu) => (
          <div key={nu.key} className="nutrient-item">
            <span className="nutrient-label">{nu.label}</span>
            <span className="nutrient-value">{nu.value} <small>{nu.unit}</small></span>
          </div>
        ))}
      </div>
    </div>
  );
}

function MealPlanSection({ stage, t, lang }) {
  const [activeDay, setActiveDay] = useState(0);

  if (!stage.has_meal_plan) {
    const msg = lang === "vi" ? stage.no_plan_note_vi : stage.no_plan_note_en;
    return (
      <div className="meal-plan-section">
        <h3 className="meal-plan-title">{t("feeding.meal_plan.title")}</h3>
        <p className="meal-plan-no-plan">{msg || t("feeding.meal_plan.no_plan")}</p>
      </div>
    );
  }

  const plan = stage.meal_plan;
  const day = plan[activeDay];

  const meals = [
    { key: "breakfast", label: t("feeding.meal_plan.breakfast"), food: lang === "vi" ? day.breakfast_vi : day.breakfast_en },
    { key: "snack_am", label: t("feeding.meal_plan.snack_am"), food: lang === "vi" ? day.snack_am_vi : day.snack_am_en },
    { key: "lunch", label: t("feeding.meal_plan.lunch"), food: lang === "vi" ? day.lunch_vi : day.lunch_en },
    { key: "snack_pm", label: t("feeding.meal_plan.snack_pm"), food: lang === "vi" ? day.snack_pm_vi : day.snack_pm_en },
    { key: "dinner", label: t("feeding.meal_plan.dinner"), food: lang === "vi" ? day.dinner_vi : day.dinner_en },
  ];

  return (
    <div className="meal-plan-section">
      <h3 className="meal-plan-title">{t("feeding.meal_plan.title")}</h3>
      <div className="day-tabs">
        {plan.map((d, i) => (
          <button
            key={i}
            className={`day-tab${activeDay === i ? " active" : ""}`}
            onClick={() => setActiveDay(i)}
          >
            {lang === "vi" ? d.day_vi : d.day_en}
          </button>
        ))}
      </div>
      <div className="meal-rows">
        {meals.map((m) => (
          <div key={m.key} className="meal-row">
            <span className="meal-label">{m.label}</span>
            <span className="meal-food">{m.food}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function FeedingGuide({ baby }) {
  const { t, lang } = useI18n();
  const [guidance, setGuidance] = useState(null);
  const [nutrition, setNutrition] = useState(null);
  const age = ageMonths(baby.birth_date);

  useEffect(() => {
    Promise.all([api.refFeeding(), api.refFeedingNutrition()]).then(
      ([g, n]) => {
        setGuidance(g);
        setNutrition(n);
      }
    );
  }, []);

  if (!guidance || !nutrition) return <div className="panel">…</div>;

  const activeNutritionStage = nutrition.stages.find(
    (s) => age >= s.age_start_months && age < s.age_end_months
  );

  return (
    <div className="panel">
      <div className="panel-header">
        <h2>{t("feeding.title")}</h2>
      </div>

      <ul className="feeding-list">
        {guidance.stages.map((stage) => {
          const isActive =
            age >= stage.age_start_months && age < stage.age_end_months;
          const title = lang === "vi" ? stage.title_vi : stage.title_en;
          const recs =
            lang === "vi"
              ? stage.recommendations_vi
              : stage.recommendations_en;
          return (
            <li
              key={stage.key}
              className={`feeding-stage ${isActive ? "active" : ""}`}
            >
              <div className="feeding-head">
                <h3>{title}</h3>
                {isActive && (
                  <span className="status-pill status-active">
                    {t("feeding.active_stage")}
                  </span>
                )}
              </div>
              <ul>
                {recs.map((line, i) => (
                  <li key={i}>{line}</li>
                ))}
              </ul>
            </li>
          );
        })}
      </ul>

      {activeNutritionStage && (
        <>
          <NutritionCard stage={activeNutritionStage} t={t} lang={lang} />
          <MealPlanSection stage={activeNutritionStage} t={t} lang={lang} />
        </>
      )}
    </div>
  );
}
