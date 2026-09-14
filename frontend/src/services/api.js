import axios from "axios";

const API_BASE = "/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: {
    "Content-Type": "application/json"
  },
  timeout: 10000
});

export const getHealth = async () => {
  const res = await apiClient.get("/health");
  return res.data;
};

export const getSummary = async () => {
  const res = await apiClient.get("/analytics/summary");
  return res.data;
};

export const getDistricts = async () => {
  const res = await apiClient.get("/analytics/districts");
  return res.data;
};

export const getCrops = async () => {
  const res = await apiClient.get("/analytics/crops");
  return res.data;
};

export const getHistoricalTrends = async (district, crop) => {
  const res = await apiClient.get("/analytics/historical", {
    params: { district, crop }
  });
  return res.data;
};

export const getModelBenchmarks = async () => {
  const res = await apiClient.get("/analytics/benchmarks");
  return res.data;
};

export const predictHarvest = async (payload) => {
  const res = await apiClient.post("/predict", payload);
  return res.data;
};

export const predictBatch = async (items) => {
  const res = await apiClient.post("/predict/batch", { items });
  return res.data;
};

export default apiClient;
