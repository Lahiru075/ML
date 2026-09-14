import React, { useState } from "react";
import { Calculator, ArrowRight, CheckCircle2, AlertCircle, Info } from "lucide-react";
import { predictHarvest } from "../services/api";

const STAPLE_CROPS = [
  "Potato",
  "Maize",
  "Kurakkan",
  "Green Gram",
  "Chili",
  "Sweet Potato",
  "Cassava"
];

export default function PredictorCard({ selectedDistrict, onForecastComplete }) {
  const [district, setDistrict] = useState(selectedDistrict || "Nuwara Eliya");
  const [season, setSeason] = useState("Maha");
  const [crop, setCrop] = useState("Potato");
  const [extentHa, setExtentHa] = useState(150.0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [prediction, setPrediction] = useState(null);

  React.useEffect(() => {
    if (selectedDistrict) {
      setDistrict(selectedDistrict);
    }
  }, [selectedDistrict]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const payload = {
        district,
        season,
        crop,
        extent_ha: parseFloat(extentHa),
        year: 2024
      };
      const result = await predictHarvest(payload);
      setPrediction(result);
      if (onForecastComplete) onForecastComplete(result);
    } catch (err) {
      setError(err.response?.data?.detail || "Prediction request failed. Please check inputs.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-panel" style={{ padding: "1.8rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1.4rem" }}>
        <Calculator size={22} style={{ color: "var(--primary)" }} />
        <div>
          <h3 style={{ fontSize: "1.2rem" }}>Highland Harvest Yield Predictor</h3>
          <p style={{ fontSize: "0.82rem", color: "var(--text-secondary)" }}>
            Trained on 25 years of Census and Statistics microclimate records
          </p>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label className="form-label">Highland District</label>
          <select
            className="form-control"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          >
            <option value="Nuwara Eliya">Nuwara Eliya</option>
            <option value="Badulla">Badulla</option>
            <option value="Kandy">Kandy</option>
            <option value="Matale">Matale</option>
            <option value="Moneragala">Moneragala</option>
          </select>
        </div>

        <div className="grid-2">
          <div className="form-group">
            <label className="form-label">Cultivation Season</label>
            <select
              className="form-control"
              value={season}
              onChange={(e) => setSeason(e.target.value)}
            >
              <option value="Maha">Maha (NE Monsoon, Sep-Mar)</option>
              <option value="Yala">Yala (SW Monsoon, May-Aug)</option>
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Crop Variety</label>
            <select
              className="form-control"
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
            >
              {STAPLE_CROPS.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="form-group">
          <label className="form-label">Cultivated Extent (Hectares)</label>
          <input
            type="number"
            min="0.1"
            step="0.5"
            className="form-control"
            value={extentHa}
            onChange={(e) => setExtentHa(e.target.value)}
            required
          />
          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "0.3rem" }}>
            Enter planned land area allocated for cultivation.
          </div>
        </div>

        <button type="submit" className="btn-primary" disabled={loading}>
          {loading ? "Computing Forecast..." : (
            <>
              Generate ML Harvest Prediction <ArrowRight size={18} />
            </>
          )}
        </button>
      </form>

      {error && (
        <div style={{ marginTop: "1.2rem", padding: "0.8rem", borderRadius: "var(--radius-sm)", background: "hsla(346, 84%, 61%, 0.15)", border: "1px solid var(--accent-rose)", color: "var(--text-primary)", display: "flex", gap: "0.5rem", alignItems: "center" }}>
          <AlertCircle size={18} style={{ color: "var(--accent-rose)" }} />
          <span style={{ fontSize: "0.88rem" }}>{error}</span>
        </div>
      )}

      {prediction && (
        <div className="forecast-result-box">
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <span style={{ fontSize: "0.82rem", textTransform: "uppercase", color: "var(--text-secondary)", letterSpacing: "0.05em", fontWeight: 600 }}>
              Forecast Output ({prediction.district} • {prediction.season})
            </span>
            <span style={{ fontSize: "0.78rem", background: "hsla(152, 68%, 46%, 0.2)", color: "var(--primary)", padding: "0.2rem 0.6rem", borderRadius: "var(--radius-full)", fontWeight: 600 }}>
              {prediction.crop_category}
            </span>
          </div>

          <div style={{ marginTop: "0.8rem" }}>
            <div className="forecast-val">{prediction.predicted_production_mt?.toLocaleString()} MT</div>
            <div style={{ fontSize: "0.95rem", color: "var(--text-secondary)", marginTop: "0.2rem" }}>
              Estimated Crop Yield: <strong style={{ color: "var(--text-primary)" }}>{prediction.predicted_yield_mt_per_ha} MT / Hectare</strong>
            </div>
            <div className="forecast-interval">
              90% CI: {prediction.confidence_interval?.lower_mt?.toLocaleString()} MT – {prediction.confidence_interval?.upper_mt?.toLocaleString()} MT
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
