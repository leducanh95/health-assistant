import { useEffect, useState } from "react";
import { api } from "../api.js";
import { useI18n } from "../i18n/index.jsx";

export default function GrowthReferenceTable({ sex }) {
  const { t } = useI18n();
  const [open, setOpen] = useState(false);
  const [tableData, setTableData] = useState(null);

  useEffect(() => {
    setTableData(null);
  }, [sex]);

  useEffect(() => {
    if (!open || tableData) return;
    let cancelled = false;
    api
      .refGrowthTable(sex)
      .then((d) => {
        if (!cancelled) setTableData(d);
      })
      .catch(() => {});
    return () => {
      cancelled = true;
    };
  }, [open, sex, tableData]);

  return (
    <div className="ref-table-section">
      <button
        className="ref-table-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-expanded={open}
      >
        <span>{t("growth.ref_table.title")}</span>
        <span className="ref-table-toggle-icon">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <>
          <p className="ref-table-source">{t("growth.ref_table.source")}</p>
          {!tableData ? (
            <div className="chart-placeholder">…</div>
          ) : (
            <div className="ref-table-scroll">
              <table className="ref-table">
                <thead>
                  <tr>
                    <th rowSpan={2}>{t("growth.ref_table.col_age")}</th>
                    <th colSpan={3}>{t("growth.ref_table.col_weight_kg")}</th>
                    <th colSpan={3}>{t("growth.ref_table.col_length_cm")}</th>
                  </tr>
                  <tr>
                    <th>P3</th>
                    <th>P50</th>
                    <th>P97</th>
                    <th>P3</th>
                    <th>P50</th>
                    <th>P97</th>
                  </tr>
                </thead>
                <tbody>
                  {tableData.rows.map((row) => (
                    <tr key={row.age_months}>
                      <td>{row.age_months}</td>
                      <td>{row.weight.p3}</td>
                      <td className="ref-table-median">{row.weight.p50}</td>
                      <td>{row.weight.p97}</td>
                      <td>{row.length.p3}</td>
                      <td className="ref-table-median">{row.length.p50}</td>
                      <td>{row.length.p97}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      )}
    </div>
  );
}
