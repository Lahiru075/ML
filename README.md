# CropForecastLK: Sri Lanka Highland Crops Production Forecasting & Agricultural Intelligence System

[![Python 3.11](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React 18](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![XGBoost](https://img.shields.io/badge/Model-XGBoost%20Regressor-EB7234?logo=xgboost&logoColor=white)](https://xgboost.readthedocs.io/)
[![Optuna](https://img.shields.io/badge/Hyperparameter-Optuna%20TPE-2C5E8A)](https://optuna.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Academic Module**: Machine Learning Development & Full-Stack Application  
> **Target Domain**: Sri Lankan Highland Agricultural Crop Production & Yield Forecasting  
> **Execution Strategy**: Solo Developer Full-Stack Implementation & Single Linear `main` Branch Delivery

---

## 1. Executive Summary

**CropForecastLK** is an end-to-end machine learning system and web intelligence platform designed to forecast seasonal agricultural crop production and land productivity across Sri Lanka's highland districts (**Nuwara Eliya, Badulla, Kandy, Matale, and Moneragala**). 

Trained on over two decades (**2000–2025, 94,755 raw agricultural census records**) from the Department of Census and Statistics Sri Lanka, the system mitigates climate-induced crop yield volatility and supports food security planning. It bridges machine learning with a sub-50ms high-performance **FastAPI** microservice and an interactive **React + Vite** dashboard styled in dark glassmorphism.

---

## 2. Monorepo Architecture

```text
CropForecastLK/
├── data/
│   ├── raw/
│   │   └── researchData.xlsx               # Original Census dataset (94,755 rows)
│   ├── processed/
│   │   ├── cleaned_highland_crops.csv      # Sanitized records (60,750 seasonal observations)
│   │   ├── engineered_features.parquet    # Feature-engineered tabular dataset
│   │   └── engineered_features.csv        # CSV export of engineered features
│   └── artifacts/
│       ├── crop_forecaster_pipeline.joblib # Serialized production inference pipeline
│       ├── optuna_study_best_params.json   # Optimal hyperparameters discovered by Optuna
│       └── model_metadata.json             # Feature schema & holdout test metrics
├── docs/
│   ├── dataset_dictionary.md               # Variable definitions & units
│   └── architecture_diagram.md             # System flow & architectural diagram
├── ml_pipeline/
│   ├── __init__.py                         # Package exports
│   ├── config.py                           # Central configuration & seeds
│   ├── data_ingestion.py                   # Automated raw Excel ingestion & audit
│   ├── preprocessing.py                    # Regex string parser & cohort imputation
│   ├── feature_engineering.py              # Yield ratio, lags, rolling stats & target encoding
│   ├── train.py                            # 5-model benchmarking & Optuna study
│   ├── evaluate.py                         # Evaluation metrics (RMSE, MAE, R², MAPE)
│   ├── inference.py                        # Self-contained production inference engine
│   ├── export_pipeline.py                  # Joblib serialization & smoke tests
│   └── test_pipeline.py                    # Pytest test suite for ML components
├── notebooks/
│   ├── 01_problem_definition_and_eda.ipynb # Steps 1-4: Raw Profiling & Highland EDA
│   ├── 02_cleaning_and_feature_engineering.ipynb # Steps 5-9: Preprocessing & Leakage Prevention
│   ├── 03_benchmarking_crossval_evaluation.ipynb # Steps 10-13: 5 Models, TimeSeries CV & Scores
│   ├── 04_optuna_tuning_pipeline_export.ipynb    # Steps 14-15: Optuna Tuning & Export
│   └── CropForecastLK_Master_Pipeline.ipynb     # Consolidated master pipeline notebook
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── config.py                   # Pydantic settings & paths
│   │   │   └── model_loader.py             # Singleton in-memory model loader
│   │   ├── schemas/
│   │   │   └── prediction.py               # Pydantic v2 request/response schemas
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── predict.py          # /predict and /predict/batch
│   │   │       │   ├── analytics.py        # Historical trends & summary telemetry
│   │   │       │   └── health.py           # /health service status
│   │   │       └── router.py               # API v1 router
│   │   └── main.py                         # FastAPI app & CORS middleware
│   ├── tests/
│   │   ├── test_predict_api.py             # API endpoint unit tests
│   │   └── test_ml_integration.py         # Sub-50ms inference latency tests
│   ├── Dockerfile                          # Container specification
│   └── requirements.txt                    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/                     # Navbar, DistrictSelector, PredictorCard, Charts
│   │   ├── pages/                          # Dashboard, Forecasting, ModelPerformance
│   │   ├── services/api.js                 # Axios API connector
│   │   ├── index.css                       # Dark glassmorphic HSL design system
│   │   ├── App.jsx                         # Root application component
│   │   └── main.jsx                        # React 18 DOM mount
│   ├── package.json                        # Node dependencies
│   └── vite.config.js                      # Vite proxy and build configuration
├── .gitignore
└── README.md
```

---

## 3. Machine Learning Methodology (15 Steps)

```mermaid
flowchart LR
    A["Raw Excel (94,755 rows)"] --> B["Phase 1: Ingestion & EDA"]
    B --> C["Phase 2: Cleaning & Features"]
    C --> D["Phase 3: 5-Model Benchmarking"]
    D --> E["Phase 4: Optuna Tuning & Packaging"]
    E --> F["FastAPI Microservice (<5ms Inference)"]
    F --> G["React + Vite UI"]
```

### Steps Implemented:
1. **Problem Definition**: Multivariate regression predicting total seasonal harvest (`Production` in Metric Tons) and agricultural yield (`Crop_Yield` in MT/Ha).
2. **Automated Ingestion**: Schema audit and loading of 94,755 rows spanning 2001–2025.
3. **Descriptive Profiling**: Identified comma thousands separators, missing placeholders (`"-"`, `"n.a."`), and severe distribution skewness.
4. **Seasonal & Geographic EDA**: Profiled monsoon regimes: **Maha** (NE Monsoon, primary season) vs. **Yala** (SW Monsoon, dry spell risks).
5. **Regex String Sanitization**: Stripped non-numeric formatting and eliminated aggregate national rows.
6. **Outlier Handling & Cohort Imputation**: Filtered biological anomalies (`Extent=0, Production>0`) and applied 4-tier cohort median imputation (`[District, Crop, Season]`).
7. **Lag & Rolling Features**: 1-Year temporal lags (`Production_Lag_1Y`, `Yield_Lag_1Y`, `Extent_Lag_1Y`) and 3-Year rolling statistics (`Extent_RollMean_3Y`, `Extent_RollStd_3Y`).
8. **Smoothed Target Encoding**: Computed out-of-fold smoothed encodings strictly on the training partition ($m = 10.0$) to eliminate data leakage.
9. **Strict Chronological Splitting**:
   - **Training Set (<= 2017)**: 40,346 records.
   - **Validation Set (2018–2020)**: 7,572 records.
   - **Holdout Test Set (2021–2025)**: 12,832 records.
10. **5-Model Comparative Benchmarking**: Ridge Regression, Random Forest, CatBoost, LightGBM, and XGBoost.
11. **Time-Series Cross-Validation**: 5-fold expanding window cross-validation across temporal boundaries.
12. **Standardized Metrics**: Evaluation across RMSE, MAE, R², and MAPE.
13. **Residual & SHAP Diagnostics**: Error distribution auditing and TreeSHAP feature importance ranking.
14. **Optuna Bayesian Optimization**: 35-trial study with `TPESampler` driving validation RMSE down to 1201.10.
15. **Production Serialization**: Self-contained inference pipeline serialized to `data/artifacts/crop_forecaster_pipeline.joblib`.

---

## 4. Model Benchmarking Scorecard

| Model | Validation RMSE (MT) | Validation MAE (MT) | Validation $R^2$ Score | Fit Time (s) | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Champion)** | **1,201.10** | **245.08** | **0.8637** | 1.43s | **Production Model** |
| **CatBoost Regressor** | 1,447.17 | 329.48 | 0.8335 | 3.88s | Benchmarked |
| **Ridge Regression** | 2,531.86 | 848.60 | 0.4904 | 0.13s | Baseline |
| **LightGBM Regressor** | 3,185.74 | 358.91 | 0.1932 | 0.89s | Benchmarked |
| **Random Forest** | 4,481.91 | 336.89 | -0.5970 | 8.82s | Benchmarked |

*Holdout Test Performance (2021–2025 Unseen Future Data): $R^2 = 0.7465$, $\text{MAE} = 227.8\text{ MT}$.*

---

## 5. Quickstart & Installation

### Prerequisites
- Python 3.11 installed
- Node.js v18+ & npm

### 1. Backend Setup
```bash
# Clone and enter directory
cd e:/Lahiru

# Create and activate Python 3.11 virtual environment
py -3.11 -m venv .venv
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run ML test suite
pytest ml_pipeline/ -v

# Run Backend test suite
pytest backend/tests/ -v

# Start FastAPI server
uvicorn backend.app.main:app --reload --port 8000
```
Interactive Swagger documentation available at: `http://localhost:8000/docs`.

### 2. Frontend Setup
```bash
cd frontend

# Install Node modules
npm install

# Verify production build
npm run build

# Start Vite development server
npm run dev
```
Dashboard available at: `http://localhost:5173`.

---

## 6. API Reference

### Single Harvest Prediction
`POST /api/v1/predict`
```json
{
  "district": "Nuwara Eliya",
  "season": "Maha",
  "crop": "Potato",
  "extent_ha": 150.0,
  "year": 2024
}
```
**Response (`< 5ms`):**
```json
{
  "district": "Nuwara Eliya",
  "season": "Maha",
  "crop": "Potato",
  "crop_category": "Up Country Vegetable",
  "extent_ha": 150.0,
  "predicted_production_mt": 5009.55,
  "predicted_yield_mt_per_ha": 33.4,
  "confidence_interval": {
    "lower_mt": 4258.12,
    "upper_mt": 5760.98
  }
}
```

---

## 7. Solo Viva Voce Defense Key Points

- **Why Supervised Regression over ARIMA?** Pure time-series models cannot take exogenous inputs such as cultivated extent (land size) or abrupt seasonal rainfall shifts. Regression with gradient boosting accounts for non-linear land-to-yield relationships augmented by temporal lag memory ($t-1$).
- **How was Data Leakage Prevented?** Enforced strict chronological splitting (Train <= 2017, Val 2018–2020, Test 2021–2025). Target encodings and rolling window stats were calculated strictly on historical training folds with out-of-fold methods.
- **Why XGBoost Outperformed Random Forest?** Tabular agricultural census records contain subtle multi-factor interactions. Gradient boosted trees optimize residuals sequentially with $L_1$/$L_2$ regularization, preventing overfitting on anomalous flood/drought seasons.
- **Microsecond Inference Architecture**: The FastAPI microservice loads `crop_forecaster_pipeline.joblib` once at startup into memory via a singleton loader (`model_loader.py`), reducing inference latency to under 5ms.
