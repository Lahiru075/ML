import React, { useState, useEffect } from "react";
import { Cpu, Award, Zap, GitBranch, BarChart2 } from "lucide-react";
import { getModelBenchmarks } from "../services/api";
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from "recharts";

export default function ModelPerformance() {
  const [metadata, setMetadata] = useState(null);

  useEffect(() => {
    getModelBenchmarks().then(setMetadata).catch(console.error);
  }, []);

  const benchmarkTable = [
    { name: "XGBoost (Champion)", rmse: 1201.10, mae: 245.08, r2: 0.8637, time: "1.43s", status: "Production Model" },
    { name: "CatBoost Regressor", rmse: 1447.17, mae: 329.48, r2: 0.8335, time: "3.88s", status: "Benchmarked" },
    { name: "Ridge Regression", rmse: 2531.86, mae: 848.60, r2: 0.4904, time: "0.13s", status: "Baseline" },
    { name: "LightGBM Regressor", rmse: 3185.74, mae: 358.91, r2: 0.1932, time: "0.89s", status: "Benchmarked" },
    { name: "Random Forest", rmse: 4481.91, mae: 336.89, r2: -0.5970, time: "8.82s", status: "Benchmarked" }
  ];

  // Format feature importances for chart
  const featureData = metadata?.feature_importances
    ? Object.entries(metadata.feature_importances).map(([k, v]) => ({
        feature: k.replace("_TargetEnc", " (Enc)").replace("_1Y", " Lag-1Y"),
        importance: v
      })).sort((a, b) => b.importance - a.importance)
    : [];

  return (
    <div className="container">
      <div style={{ marginBottom: "1.8rem" }}>
        <h1 className="page-title">Model Benchmarks, SHAP & Optimization</h1>
        <p className="page-subtitle">
          Rigorous 5-model evaluation harness, Time-Series Cross Validation, and Optuna hyperparameter telemetry.
        </p>
      </div>

      <div className="grid-3" style={{ marginBottom: "2rem" }}>
        <div className="glass-panel kpi-card">
          <div className="kpi-icon-wrap" style={{ color: "var(--primary)" }}>
            <Award size={26} />
          </div>
          <div>
            <div className="kpi-title">Champion Algorithm</div>
            <div className="kpi-value" style={{ fontSize: "1.35rem" }}>XGBoost + Optuna</div>
            <div className="kpi-sub">Holdout R²: <strong>{metadata?.holdout_test_metrics?.R2 || 0.7465}</strong></div>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-icon-wrap" style={{ color: "var(--accent-cyan)" }}>
            <Zap size={26} />
          </div>
          <div>
            <div className="kpi-title">Inference Speed</div>
            <div className="kpi-value" style={{ fontSize: "1.35rem" }}>&lt; 5 ms</div>
            <div className="kpi-sub">In-RAM Singleton Model Loader</div>
          </div>
        </div>

        <div className="glass-panel kpi-card">
          <div className="kpi-icon-wrap" style={{ color: "var(--accent-amber)" }}>
            <GitBranch size={26} />
          </div>
          <div>
            <div className="kpi-title">Validation Protocol</div>
            <div className="kpi-value" style={{ fontSize: "1.35rem" }}>5-Fold TimeSeries CV</div>
            <div className="kpi-sub">Strict Out-of-Fold Chronological Split</div>
          </div>
        </div>
      </div>

      <div className="glass-panel" style={{ padding: "1.8rem", marginBottom: "2rem" }}>
        <h3 style={{ fontSize: "1.15rem", marginBottom: "1rem" }}>5-Model Comparative Benchmarking Scorecard</h3>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.92rem" }}>
            <thead>
              <tr style={{ borderBottom: "1px solid var(--glass-border)", color: "var(--text-secondary)", textAlign: "left" }}>
                <th style={{ padding: "0.75rem" }}>Algorithm</th>
                <th style={{ padding: "0.75rem" }}>RMSE (MT)</th>
                <th style={{ padding: "0.75rem" }}>MAE (MT)</th>
                <th style={{ padding: "0.75rem" }}>R² Score</th>
                <th style={{ padding: "0.75rem" }}>Fit Time</th>
                <th style={{ padding: "0.75rem" }}>Status</th>
              </tr>
            </thead>
            <tbody>
              {benchmarkTable.map((row, idx) => (
                <tr key={idx} style={{
                  borderBottom: "1px solid hsla(210, 40%, 98%, 0.04)",
                  backgroundColor: row.name.includes("Champion") ? "hsla(152, 68%, 46%, 0.08)" : "transparent"
                }}>
                  <td style={{ padding: "0.75rem", fontWeight: 700, color: row.name.includes("Champion") ? "var(--primary)" : "var(--text-primary)" }}>
                    {row.name}
                  </td>
                  <td style={{ padding: "0.75rem", fontFamily: "var(--font-mono)" }}>{row.rmse.toFixed(2)}</td>
                  <td style={{ padding: "0.75rem", fontFamily: "var(--font-mono)" }}>{row.mae.toFixed(2)}</td>
                  <td style={{ padding: "0.75rem", fontFamily: "var(--font-mono)", fontWeight: 700, color: row.r2 > 0.8 ? "var(--primary)" : "inherit" }}>
                    {row.r2.toFixed(4)}
                  </td>
                  <td style={{ padding: "0.75rem", fontFamily: "var(--font-mono)", color: "var(--text-muted)" }}>{row.time}</td>
                  <td style={{ padding: "0.75rem" }}>
                    <span style={{
                      fontSize: "0.78rem",
                      padding: "0.25rem 0.6rem",
                      borderRadius: "var(--radius-full)",
                      background: row.name.includes("Champion") ? "hsla(152, 68%, 46%, 0.2)" : "hsla(215, 20%, 65%, 0.15)",
                      color: row.name.includes("Champion") ? "var(--primary)" : "var(--text-secondary)",
                      fontWeight: 600
                    }}>
                      {row.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="grid-2">
        <div className="glass-panel" style={{ padding: "1.8rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.2rem" }}>
            <BarChart2 size={20} style={{ color: "var(--primary)" }} />
            <h3 style={{ fontSize: "1.15rem" }}>Feature Importance & Drivers</h3>
          </div>
          <div style={{ width: "100%", height: 320 }}>
            <ResponsiveContainer>
              <BarChart data={featureData} layout="vertical" margin={{ top: 10, right: 30, left: 40, bottom: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="hsla(210, 40%, 98%, 0.05)" />
                <XAxis type="number" stroke="var(--text-muted)" fontSize={11} />
                <YAxis dataKey="feature" type="category" stroke="var(--text-muted)" fontSize={11} width={130} />
                <Tooltip
                  formatter={(val) => [(val * 100).toFixed(2) + "%", "Importance"]}
                  contentStyle={{ background: "hsla(218, 28%, 13%, 0.95)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)" }}
                />
                <Bar dataKey="importance" fill="var(--primary)" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-panel" style={{ padding: "1.8rem" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.2rem" }}>
            <Cpu size={20} style={{ color: "var(--accent-cyan)" }} />
            <h3 style={{ fontSize: "1.15rem" }}>Optuna Hyperparameter Exploration</h3>
          </div>
          <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)", marginBottom: "1rem" }}>
            Automated 35-trial Bayesian optimization study using Tree-structured Parzen Estimator (TPE) targeting minimum Cross-Validation RMSE.
          </p>

          <div style={{ background: "hsla(218, 28%, 11%, 0.85)", border: "1px solid var(--glass-border)", borderRadius: "var(--radius-md)", padding: "1rem", fontFamily: "var(--font-mono)", fontSize: "0.82rem" }}>
            <div style={{ color: "var(--accent-cyan)", marginBottom: "0.5rem" }}>// Optimal Parameters Discovered</div>
            <pre style={{ color: "var(--text-primary)", whiteSpace: "pre-wrap" }}>
              {JSON.stringify(metadata?.best_hyperparameters || {}, null, 2)}
            </pre>
          </div>
        </div>
      </div>
    </div>
  );
}
