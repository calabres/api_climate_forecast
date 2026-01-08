# 🌦️ Climate Viewer API - Buenos Aires

**An Interactive Seasonal Forecast Skill Monitor & Smart Recommendation System**

[![AI-Powered](https://img.shields.io/badge/AI-Powered-purple?style=flat-square)](https://github.com/calabres/api_climate_forecast)
[![Status](https://img.shields.io/badge/Status-Prototype-green?style=flat-square)]()
[![Stack](https://img.shields.io/badge/Stack-Django%20%7C%20Xarray%20%7C%20Leaflet-blue?style=flat-square)]()

## 📖 Problem Description
Seasonal climate forecasting is crucial for agriculture and water management in the **Pampas Region (Argentina)**. However, different global climate models (ECMWF, NCEP, UKMO, etc.) perform differently depending on the specific location and time of year.

Currently, stakeholders struggle to:
1. Identify which global model is trustworthy for their specific farm/location.
2. Visualize the forecast bias (mm) and skill (correlation) in a simple interface.
3. Obtain a consolidated "Smart Forecast" based on the historically best-performing model.

**Climate Viewer API** solves this by processing 24 years of hindcast data (1993-2016) to evaluate 8 major climate agencies and recommend the optimal forecast source for every month and coordinate in Buenos Aires.

## 🤖 AI-Assisted Development
This project was built using an **Agentic AI Workflow** (Antigravity).
- **Role of AI:** The AI acted as a pair programmer, handling complex tasks such as:
    - Normalizing inconsistent NetCDF naming conventions across 8 different climate centers (e.g., handling `tprate` vs `precip`, `forecastMonth` vs `lead_time`).
    - Implementing a serverless-style data processing pipeline in Django to manage memory efficienty.
    - Generating the frontend logic for dynamic charts and maps.
- **Workflow:** Iterative loop of Problem Definition -> AI Implementation -> User Review -> Git Integration.

## 🛠️ Technology Stack
### Backend
- **Framework:** Python / Django 4.2
- **Data Engine:** Xarray & Dask (for efficient lazy-loading of NetCDF files).
- **Analysis:** SciPy (Pearson Correlation), NumPy (Bias calculation).
- **API:** Django Rest Framework (JSON endpoints).

### Frontend
- **Interface:** HTML5 / CSS3 (Inter font, Cream palette).
- **Maps:** Leaflet.js (Interactive selection of coordinates).
- **Charts:** Chart.js (Visualization of forecast vs climatology).

### Data Source
- **Copernicus Climate Change Service (C3S):** Seasonal Hindcasts (1993-2016) and ERA5 Reanalysis.
- **Models Integrated:** ECMWF, NCEP, UKMO, JMA, Météo-France, DWD, CMCC, ECCC.

## 🚀 How to Run

### Prerequisites
- Python 3.9+
- Git

### Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/calabres/api_climate_forecast.git
   cd api_climate_forecast
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. **Data Setup:**
   Ensure the `data_bsas/` folder is populated with the NetCDF files (ERA5 and Hindcasts). 
   *(Note: Data is not included in the repo due to size -> 50GB+).*

4. Run the Server:
   ```bash
   cd web_platform
   python manage.py runserver
   ```

5. Access:
   Open browser at `http://127.0.0.1:8000/`

## 📡 API Endpoints

### 1. Skill Matrix
**GET** `/api/skill?lat=-34.6&lon=-58.4&month=1`
Returns historical performance metrics for all models.
```json
{
  "acc": { "ecmwf": [0.5, 0.4, ...], ... },
  "bias": { "ecmwf": [10.5, -2.0, ...], ... }
}
```

### 2. Smart Forecast
**GET** `/api/smart_forecast?lat=-34.6&lon=-58.4&month=1`
Returns the recommended best model for each lead time and its forecast.
```json
[
  {
    "mes": "Feb",
    "mejor_modelo": "NCEP",
    "skill": 0.52,
    "acumulado_mm": 125,
    "anomalia_mm": 15
  },
  ...
]
```

---
**Course Project:** AI Dev Tools Zoomcamp 2025