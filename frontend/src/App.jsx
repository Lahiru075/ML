import React, { useState, useEffect } from "react";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Forecasting from "./pages/Forecasting";
import ModelPerformance from "./pages/ModelPerformance";
import { getHealth } from "./services/api";

export default function App() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [healthStatus, setHealthStatus] = useState(null);

  useEffect(() => {
    getHealth().then(setHealthStatus).catch(console.error);
    const interval = setInterval(() => {
      getHealth().then(setHealthStatus).catch(console.error);
    }, 15000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column" }}>
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        healthStatus={healthStatus}
      />

      <main style={{ flex: 1 }}>
        {activeTab === "dashboard" && <Dashboard />}
        {activeTab === "forecasting" && <Forecasting />}
        {activeTab === "performance" && <ModelPerformance />}
      </main>

      <footer style={{
        padding: "1.8rem",
        textAlign: "center",
        borderTop: "1px solid var(--glass-border)",
        background: "hsla(218, 28%, 10%, 0.8)",
        color: "var(--text-muted)",
        fontSize: "0.85rem",
        marginTop: "3rem"
      }}>
        <div>CropForecastLK • Sri Lanka Highland Crops Production & Yield Intelligence Platform</div>
        <div style={{ marginTop: "0.3rem", fontSize: "0.78rem" }}>
          Department of Census and Statistics (2000–2025) • Machine Learning & Full-Stack Application
        </div>
      </footer>
    </div>
  );
}
