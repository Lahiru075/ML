import React, { useState } from "react";
import { Sliders, Sparkles, Plus, Trash2 } from "lucide-react";
import PredictorCard from "../components/PredictorCard";
import { predictBatch } from "../services/api";

export default function Forecasting() {
  const [simulations, setSimulations] = useState([
    { district: "Nuwara Eliya", season: "Maha", crop: "Potato", extent_ha: 150.0 },
    { district: "Badulla", season: "Yala", crop: "Maize", extent_ha: 180.0 },
    { district: "Kandy", season: "Maha", crop: "Cassava", extent_ha: 90.0 }
  ]);
  const [batchResults, setBatchResults] = useState([]);
  const [runningBatch, setRunningBatch] = useState(false);

  const runSimulations = async () => {
    setRunningBatch(true);
    try {
      const res = await predictBatch(simulations);
      setBatchResults(res.predictions || []);
    } catch (e) {
      console.error(e);
    } finally {
      setRunningBatch(false);
    }
  };

  return (
    <div className="container">
      <div style={{ marginBottom: "1.8rem" }}>
        <h1 className="page-title">Highland Harvest Forecasting Engine</h1>
        <p className="page-subtitle">
          Run single-scenario projections or simulate multi-district seasonal allocations simultaneously.
        </p>
      </div>

      <div className="grid-2" style={{ marginBottom: "2rem" }}>
        <PredictorCard selectedDistrict="Nuwara Eliya" />

        <div className="glass-panel" style={{ padding: "1.8rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.2rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
              <Sliders size={20} style={{ color: "var(--accent-cyan)" }} />
              <h3 style={{ fontSize: "1.15rem" }}>Multi-District Scenario Batch Simulation</h3>
            </div>
            <button
              onClick={runSimulations}
              disabled={runningBatch}
              style={{
                background: "var(--accent-cyan)",
                color: "#0b1320",
                border: "none",
                padding: "0.5rem 1rem",
                borderRadius: "var(--radius-full)",
                fontWeight: 700,
                fontSize: "0.85rem",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                gap: "0.4rem"
              }}
            >
              <Sparkles size={16} /> {runningBatch ? "Simulating..." : "Run Batch Simulation"}
            </button>
          </div>

          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.88rem" }}>
              <thead>
                <tr style={{ borderBottom: "1px solid var(--glass-border)", color: "var(--text-secondary)", textAlign: "left" }}>
                  <th style={{ padding: "0.6rem" }}>District</th>
                  <th style={{ padding: "0.6rem" }}>Season</th>
                  <th style={{ padding: "0.6rem" }}>Crop</th>
                  <th style={{ padding: "0.6rem" }}>Extent (Ha)</th>
                </tr>
              </thead>
              <tbody>
                {simulations.map((s, idx) => (
                  <tr key={idx} style={{ borderBottom: "1px solid hsla(210, 40%, 98%, 0.04)" }}>
                    <td style={{ padding: "0.6rem", fontWeight: 600 }}>{s.district}</td>
                    <td style={{ padding: "0.6rem" }}>{s.season}</td>
                    <td style={{ padding: "0.6rem" }}>{s.crop}</td>
                    <td style={{ padding: "0.6rem", fontFamily: "var(--font-mono)" }}>{s.extent_ha}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {batchResults.length > 0 && (
            <div style={{ marginTop: "1.4rem" }}>
              <h4 style={{ fontSize: "0.95rem", color: "var(--primary)", marginBottom: "0.6rem" }}>Simulation Results:</h4>
              <div style={{ display: "grid", gap: "0.6rem" }}>
                {batchResults.map((r, idx) => (
                  <div key={idx} style={{ padding: "0.8rem", borderRadius: "var(--radius-sm)", background: "hsla(218, 25%, 22%, 0.6)", border: "1px solid var(--glass-border)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <strong>{r.district}</strong> • {r.crop} ({r.season})
                      <div style={{ fontSize: "0.78rem", color: "var(--text-muted)" }}>Yield: {r.predicted_yield_mt_per_ha} MT/Ha</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <span style={{ fontSize: "1.1rem", fontWeight: 800, color: "var(--primary)", fontFamily: "var(--font-mono)" }}>
                        {r.predicted_production_mt?.toLocaleString()} MT
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
