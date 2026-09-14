import React from "react";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  CartesianGrid
} from "recharts";
import { BarChart2 } from "lucide-react";

export default function AnalyticsChart({ historicalData, district, crop }) {
  if (!historicalData || historicalData.length === 0) {
    return (
      <div className="glass-panel" style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)" }}>
        No historical records available for {crop} in {district}.
      </div>
    );
  }

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          background: "hsla(218, 28%, 13%, 0.95)",
          border: "1px solid var(--glass-border)",
          borderRadius: "var(--radius-md)",
          padding: "0.8rem 1rem",
          boxShadow: "var(--shadow-card)",
          fontFamily: "var(--font-sans)"
        }}>
          <div style={{ fontWeight: 700, marginBottom: "0.3rem", color: "var(--text-primary)" }}>
            Year {label}
          </div>
          <div style={{ color: "var(--primary)", fontSize: "0.85rem" }}>
            Maha Production: <strong>{payload[0]?.value?.toLocaleString()} MT</strong>
          </div>
          <div style={{ color: "var(--accent-cyan)", fontSize: "0.85rem" }}>
            Yala Production: <strong>{payload[1]?.value?.toLocaleString()} MT</strong>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="glass-panel" style={{ padding: "1.8rem" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.2rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
          <BarChart2 size={20} style={{ color: "var(--accent-cyan)" }} />
          <div>
            <h3 style={{ fontSize: "1.15rem" }}>Historical Seasonal Production Trends</h3>
            <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
              Comparing Maha vs. Yala Harvests for {crop} in {district} (2001–2025)
            </p>
          </div>
        </div>
      </div>

      <div style={{ width: "100%", height: 340 }}>
        <ResponsiveContainer>
          <BarChart data={historicalData} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="hsla(210, 40%, 98%, 0.05)" />
            <XAxis dataKey="year" stroke="var(--text-muted)" fontSize={11} tickLine={false} />
            <YAxis stroke="var(--text-muted)" fontSize={11} tickLine={false} unit=" MT" />
            <Tooltip content={<CustomTooltip />} />
            <Legend wrapperStyle={{ paddingTop: "10px" }} />
            <Bar dataKey="maha_production_mt" name="Maha Season (NE Monsoon)" fill="var(--primary)" radius={[4, 4, 0, 0]} />
            <Bar dataKey="yala_production_mt" name="Yala Season (SW Monsoon)" fill="var(--accent-cyan)" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
