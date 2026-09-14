import React from "react";
import { Mountain, CheckCircle } from "lucide-react";

const HIGHLAND_META = [
  { name: "Nuwara Eliya", elevation: "1,868m", specialty: "Highland Potato, Up-country Vegetables", zone: "Central Highlands" },
  { name: "Badulla", elevation: "680m", specialty: "Maize, Hill Country Legumes", zone: "Uva Highlands" },
  { name: "Kandy", elevation: "500m", specialty: "Cassava, Minor Export Spices", zone: "Central Foothills" },
  { name: "Matale", elevation: "364m", specialty: "Chili, Onion, Green Gram", zone: "Knuckles Range" },
  { name: "Moneragala", elevation: "150m-600m", specialty: "Kurakkan, Traditional Grains", zone: "Highland Transition Zone" }
];

export default function DistrictSelector({ selectedDistrict, onSelectDistrict }) {
  return (
    <div className="glass-panel" style={{ padding: "1.5rem", marginBottom: "2rem" }}>
      <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginBottom: "1rem" }}>
        <Mountain size={20} style={{ color: "var(--primary)" }} />
        <h3 style={{ fontSize: "1.1rem" }}>Highland Agricultural Focus Districts</h3>
      </div>
      
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(210px, 1fr))", gap: "0.85rem" }}>
        {HIGHLAND_META.map((item) => {
          const isSelected = selectedDistrict === item.name;
          return (
            <div
              key={item.name}
              className={`district-pill ${isSelected ? "selected" : ""}`}
              onClick={() => onSelectDistrict(item.name)}
              style={{
                flexDirection: "column",
                alignItems: "flex-start",
                padding: "0.9rem",
                cursor: "pointer"
              }}
            >
              <div style={{ display: "flex", justifyContent: "space-between", width: "100%", alignItems: "center" }}>
                <span style={{ fontWeight: 700, color: isSelected ? "var(--primary)" : "var(--text-primary)" }}>
                  {item.name}
                </span>
                {isSelected && <CheckCircle size={16} style={{ color: "var(--primary)" }} />}
              </div>
              <div style={{ fontSize: "0.76rem", color: "var(--text-muted)", marginTop: "0.2rem" }}>
                {item.elevation} • {item.zone}
              </div>
              <div style={{ fontSize: "0.78rem", color: "var(--text-secondary)", marginTop: "0.35rem" }}>
                {item.specialty}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
