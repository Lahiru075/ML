# CropForecastLK: Agricultural Census Dataset Dictionary

Dataset derived from Sri Lanka's Department of Census and Statistics (2000–2025 agricultural census series).

| Field Name | Type | Description | Units / Values | Example |
| :--- | :--- | :--- | :--- | :--- |
| `District` | Categorical | Sri Lankan Administrative District (25 districts) | Text | Nuwara Eliya, Badulla, Kandy |
| `Season` | Categorical | Monsoonal Agricultural Cultivation Season | `Maha` (NE Monsoon), `Yala` (SW Monsoon) | Maha |
| `CropCategory` | Categorical | Broad agronomic classification | Cereals, Up Country Vegetable, Roots and Tubers, etc. | Up Country Vegetable |
| `Crop` | Categorical | Specific crop name | 91 tracked varieties | Potato, Maize, Kurakkan |
| `Year` | Integer | Standardized harvest calendar year | 2001 - 2025 | 2024 |
| `Extent` | Float | Cultivated agricultural land area | Hectares (Ha) | 150.0 |
| `Production` | Float | Total harvested crop quantity | Metric Tons (MT) | 5,009.5 |
| `Crop_Yield` | Float | Calculated productivity ratio (Production / Extent) | Metric Tons / Hectare (MT/Ha) | 33.40 |
| `Production_Lag_1Y` | Float | Historical production from 1-year prior | Metric Tons (MT) | 4,800.0 |
| `Yield_Lag_1Y` | Float | Historical yield from 1-year prior | MT/Ha | 32.0 |
| `Extent_RollMean_3Y`| Float | 3-Year moving average of cultivated extent | Hectares (Ha) | 145.0 |
| `Extent_RollStd_3Y` | Float | 3-Year volatility of cultivated extent | Hectares (Ha) | 8.5 |
