import React from "react";
import { Database, MapPin, TrendingUp, Layers } from "lucide-react";

export default function MetricsOverview({ summary }) {
  if (!summary) return null;

  return (
    <div className="grid-4" style={{ marginBottom: "2rem" }}>
      <div className="glass-panel kpi-card">
        <div className="kpi-icon-wrap" style={{ color: "var(--primary)" }}>
          <Database size={26} />
        </div>
        <div>
          <div className="kpi-title">Census Records</div>
          <div className="kpi-value">{summary.total_historical_records?.toLocaleString()}</div>
          <div className="kpi-sub">{summary.year_min} – {summary.year_max} Agricultural Census</div>
        </div>
      </div>

      <div className="glass-panel kpi-card">
        <div className="kpi-icon-wrap" style={{ color: "var(--accent-cyan)" }}>
          <Layers size={26} />
        </div>
        <div>
          <div className="kpi-title">Total Cultivated Extent</div>
          <div className="kpi-value">{(summary.total_extent_ha / 1000)?.toFixed(1)}k Ha</div>
          <div className="kpi-sub">Across {summary.total_districts} Districts</div>
        </div>
      </div>

      <div className="glass-panel kpi-card">
        <div className="kpi-icon-wrap" style={{ color: "var(--accent-amber)" }}>
          <TrendingUp size={26} />
        </div>
        <div>
          <div className="kpi-title">Historical Production</div>
          <div className="kpi-value">{(summary.total_production_mt / 1000)?.toFixed(1)}k MT</div>
          <div className="kpi-sub">Aggregated Highland & Lowland</div>
        </div>
      </div>

      <div className="glass-panel kpi-card">
        <div className="kpi-icon-wrap" style={{ color: "var(--primary)" }}>
          <MapPin size={26} />
        </div>
        <div>
          <div className="kpi-title">National Mean Yield</div>
          <div className="kpi-value">{summary.national_mean_yield_mt_per_ha} MT/Ha</div>
          <div className="kpi-sub">{summary.total_crops} Monitored Crop Varieties</div>
        </div>
      </div>
    </div>
  );
}
