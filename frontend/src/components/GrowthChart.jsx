import { useEffect, useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";

function ageMonthsAt(birth, on) {
  const dob = new Date(birth);
  const at = new Date(on);
  return Math.max(0, (at - dob) / (1000 * 60 * 60 * 24 * 30.4375));
}

const INDICATORS = [
  { key: "weight_for_age", field: "weight_kg" },
  { key: "length_for_age", field: "length_cm" },
  { key: "head_circumference_for_age", field: "head_circ_cm" },
];

export default function GrowthChart({ baby, indicator, history }) {
  const { t } = useI18n();
  const [curve, setCurve] = useState(null);
  const meta = INDICATORS.find((i) => i.key === indicator);

  useEffect(() => {
    let cancelled = false;
    api
      .refGrowthCurves(baby.sex, indicator)
      .then((data) => {
        if (!cancelled) setCurve(data);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [baby.sex, indicator]);

  if (!curve) return <div className="chart-placeholder">…</div>;

  const babyPoints = (history || [])
    .map((m) => ({
      age_months: Number(ageMonthsAt(baby.birth_date, m.measured_at).toFixed(2)),
      baby: m[meta.field],
    }))
    .filter((p) => p.baby != null);

  // Merge curves with baby points by age_months for plotting
  const ageMap = new Map();
  for (const p of curve.curve) ageMap.set(p.age_months, { ...p });
  for (const p of babyPoints) {
    const existing = ageMap.get(p.age_months) || { age_months: p.age_months };
    existing.baby = p.baby;
    ageMap.set(p.age_months, existing);
  }
  const data = [...ageMap.values()].sort((a, b) => a.age_months - b.age_months);

  return (
    <div className="growth-chart">
      <h3>
        {t("growth.chart_title", {
          indicator: t(`growth.indicator.${indicator}`),
        })}
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={data} margin={{ top: 8, right: 16, left: 0, bottom: 8 }}>
          <CartesianGrid stroke="#222633" strokeDasharray="3 3" />
          <XAxis
            dataKey="age_months"
            type="number"
            domain={[0, 24]}
            stroke="#9ca3af"
            label={{
              value: "months",
              position: "insideBottom",
              offset: -2,
              fill: "#9ca3af",
              fontSize: 11,
            }}
          />
          <YAxis stroke="#9ca3af" />
          <Tooltip
            contentStyle={{
              background: "#16181f",
              border: "1px solid #2a2d3a",
              fontSize: 12,
            }}
          />
          <Legend wrapperStyle={{ fontSize: 12 }} />
          <Line
            type="monotone"
            dataKey="p3"
            stroke="#ef4444"
            dot={false}
            strokeWidth={1}
            name={t("growth.legend.p3")}
          />
          <Line
            type="monotone"
            dataKey="p15"
            stroke="#eab308"
            dot={false}
            strokeWidth={1}
            strokeDasharray="4 3"
            name={t("growth.legend.p15")}
          />
          <Line
            type="monotone"
            dataKey="p85"
            stroke="#eab308"
            dot={false}
            strokeWidth={1}
            strokeDasharray="4 3"
            name={t("growth.legend.p85")}
          />
          <Line
            type="monotone"
            dataKey="p97"
            stroke="#ef4444"
            dot={false}
            strokeWidth={1}
            name={t("growth.legend.p97")}
          />
          <Line
            type="monotone"
            dataKey="p50"
            stroke="#22c55e"
            dot={false}
            strokeWidth={1.5}
            name={t("growth.legend.p50")}
          />
          <Line
            type="monotone"
            dataKey="baby"
            stroke="#3b82f6"
            strokeWidth={2.5}
            dot={{ r: 4, fill: "#3b82f6" }}
            connectNulls
            name={t("growth.legend.baby")}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
