import React, { useState, useEffect } from "react";
import MetricsOverview from "../components/MetricsOverview";
import DistrictSelector from "../components/DistrictSelector";
import PredictorCard from "../components/PredictorCard";
import AnalyticsChart from "../components/AnalyticsChart";
import { getSummary, getHistoricalTrends } from "../services/api";

export default function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [selectedDistrict, setSelectedDistrict] = useState("Nuwara Eliya");
  const [selectedCrop, setSelectedCrop] = useState("Potato");
  const [historicalData, setHistoricalData] = useState([]);
  const [loadingHistory, setLoadingHistory] = useState(false);

  useEffect(() => {
    getSummary().then(setSummary).catch(console.error);
  }, []);

  useEffect(() => {
    setLoadingHistory(true);
    getHistoricalTrends(selectedDistrict, selectedCrop)
      .then(setHistoricalData)
      .catch(console.error)
      .finally(() => setLoadingHistory(false));
  }, [selectedDistrict, selectedCrop]);

  return (
    <div className="container">
      <div style={{ marginBottom: "1.8rem" }}>
        <h1 className="page-title">Agricultural Intelligence Dashboard</h1>
        <p className="page-subtitle">
          Real-time harvest production forecasting and seasonal telemetry across Sri Lanka's highland districts.
        </p>
      </div>

      <MetricsOverview summary={summary} />

      <DistrictSelector
        selectedDistrict={selectedDistrict}
        onSelectDistrict={(dist) => setSelectedDistrict(dist)}
      />

      <div className="grid-2">
        <PredictorCard
          selectedDistrict={selectedDistrict}
          onForecastComplete={(res) => setSelectedCrop(res.crop)}
        />
        <AnalyticsChart
          historicalData={historicalData}
          district={selectedDistrict}
          crop={selectedCrop}
        />
      </div>
    </div>
  );
}
