import React from "react";
import { Sprout, Activity, BarChart3, Cpu } from "lucide-react";

export default function Navbar({ activeTab, setActiveTab, healthStatus }) {
  return (
    <header className="navbar">
      <div className="nav-brand">
        <div className="brand-icon">
          <Sprout size={24} />
        </div>
        <div>
          <div>CropForecastLK</div>
          <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", fontWeight: 400 }}>
            Sri Lanka Highland Agricultural Intelligence
          </div>
        </div>
      </div>

      <nav className="nav-links">
        <button
          className={`nav-btn ${activeTab === "dashboard" ? "active" : ""}`}
          onClick={() => setActiveTab("dashboard")}
        >
          <BarChart3 size={17} /> Dashboard
        </button>
        <button
          className={`nav-btn ${activeTab === "forecasting" ? "active" : ""}`}
          onClick={() => setActiveTab("forecasting")}
        >
          <Sprout size={17} /> Forecasting Engine
        </button>
        <button
          className={`nav-btn ${activeTab === "performance" ? "active" : ""}`}
          onClick={() => setActiveTab("performance")}
        >
          <Cpu size={17} /> Model Benchmarks & SHAP
        </button>
      </nav>

      <div className="status-badge">
        <div className="status-dot" style={{ backgroundColor: healthStatus?.model_loaded ? "var(--primary)" : "var(--accent-amber)" }} />
        <span>{healthStatus?.model_loaded ? "ML Model Active (XGBoost)" : "Connecting API..."}</span>
      </div>
    </header>
  );
}
