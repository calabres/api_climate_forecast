# 🌦️ Climate Viewer API - Buenos Aires

**An Interactive Seasonal Forecast Skill Monitor & Smart Recommendation System**

[![AI-Powered](https://img.shields.io/badge/AI-Powered-purple?style=flat-square)](https://github.com/calabres/api_climate_forecast)
[![Status](https://img.shields.io/badge/Status-Prototype-green?style=flat-square)]()
[![Stack](https://img.shields.io/badge/Stack-Django%20%7C%20Xarray%20%7C%20Leaflet-blue?style=flat-square)]()

## 📖 Problem Description
Seasonal climate forecasting is crucial for agriculture and water management in the **Pampas Region (Argentina)**. However, different global climate models (ECMWF, NCEP, UKMO, etc.) perform differently depending on the specific location and time of year.

**Climate Viewer API** allows users to view forecasts for upcoming months, serving as a key tool for strategic decision-making. It acts as a starting point for future advanced forecasting applications, such as **soil water balance models**, and complements crop simulation models used to analyze different **sowing dates or genetic cultivars**.


Currently, stakeholders struggle to:
1. Identify which global model is trustworthy for their specific farm/location.
2. Visualize the forecast bias (mm) and skill (correlation) in a simple interface.
3. Obtain a consolidated "Smart Forecast" based on the historically best-performing model.

**Climate Viewer API** solves this by processing 24 years of hindcast data (1993-2016) to evaluate 8 major climate agencies and recommend the optimal forecast source for every month and coordinate in Buenos Aires.

While these datasets are technically open, they are often difficult to access, process, and interpret for the average user. This application bridges that gap, providing a simple interface to complex scientific data.


## 🎥 Preview
![Climate App Walkthrough](docs/assets/climate_app_walkthrough_1767888624339.webp)
*(Interactive Interface: Select location -> Analyze Skill -> View Forecast)*

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

## 🌍 Integrated Climate Models
The platform integrates data from **8 major global climate centers**, processed via the Copernicus Climate Change Service (C3S). Each model has unique characteristics:

- **ECMWF SEAS5** (European Centre for Medium-Range Weather Forecasts): One of the most advanced global forecasting systems, using a coupled atmosphere-ocean-sea ice model with high resolution.
  > *Johnson, S. J., et al. (2019). SEAS5: the new ECMWF seasonal forecast system. Geoscientific Model Development, 12(3), 1087-1117.*

- **NCEP CFSv2** (National Centers for Environmental Prediction - NOAA, USA): A fully coupled model representing the interaction between the Earth's atmosphere, oceans, land, and sea ice.
  > *Saha, S., et al. (2014). The NCEP Climate Forecast System Version 2. Journal of Climate, 27(6), 2185-2208.*

- **Met Office GloSea6** (UK Met Office): Built on the HadGEM3 climate model, featuring high-resolution ocean and atmospheric components to improve prediction in the mid-latitudes.
  > *MacLachlan, C., et al. (2015). Global Seasonal forecast system version 5 (GloSea5): a high-resolution seasonal forecast system. Quarterly Journal of the Royal Meteorological Society.*

- **Météo-France System 8**: Based on the CNRM-CM climate model, integrating the ARPEGE-Climat atmosphere model and NEMO ocean model.
  > *Voldoire, A., et al. (2013). The CNRM-CM5.1 global climate model: description and basic evaluation. Climate Dynamics.*

- **DWD GCFS** (Deutscher Wetterdienst, Germany): Based on the MPI-ESM (Max Planck Institute Earth System Model), known for its robust representation of atmospheric dynamics.
  > *Baehr, J., et al. (2015). The prediction of surface temperature in the new seasonal prediction system based on the MPI-ESM coupled climate model. Climate Dynamics.*

- **CMCC SPS3.5** (Euro-Mediterranean Center on Climate Change, Italy): A coupled system improving the representation of the stratosphere and land surface processes.
  > *Sanna, A., et al. (2017). The new CMCC seasonal prediction system. Technical Report.*

- **JMA/MRI-CPS3** (Japan Meteorological Agency): Features advanced physical parameterizations for improved prediction of ENSO and Asian monsoon variability.
  > *Takaya, Y., et al. (2017). Japan Meteorological Agency/Meteorological Research Institute-Coupled Prediction System version 2 (JMA/MRI-CPS2). Climate Dynamics.*

- **ECCC CanSIPS** (Environment and Climate Change Canada): A multi-model ensemble system combining two climate models (CanCM4 and GEM-NEMO) to improve probabilistic skill.
  > *Merryfield, W. J., et al. (2013). The Canadian Seasonal to Interannual Prediction System. Part I: Models and Initialization. Monthly Weather Review.*


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
   *(Note: Total data is around 100MB in this prototype, but requires specific retrieval from C3S).*


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

## 📖 Documentation & QA
- **OpenAPI / Swagger:** Interactive API documentation is available at `/api/docs/`.
- **CI/CD:** Automated testing is implemented via **GitHub Actions**. Every push runs the test suite to ensure API contract stability.
- **Testing:** Run tests locally using `python manage.py test`.


---
**Course Project:** AI Dev Tools Zoomcamp 2025