import cdsapi

URL_CDS = "https://cds.climate.copernicus.eu/api" # Nuevo endpoint post-migración 2024
KEY_CDS = "1ed376d2-770b-495d-9637-f4825f4d7342" # Asegúrate de que esta sea tu NUEVA clave del sistema renovado

client = cdsapi.Client(url=URL_CDS, key=KEY_CDS)

dataset = "seasonal-monthly-single-levels"

# NOTA: La variable "agua en el suelo" (volumetric_soil_water_layer_1) NO está disponible
# en "monthly_mean" del conjunto estacional. Solo en datos diarios (heavy).
# Por eso, descargamos solo precipitación.

request = {
    "originating_centre": "ecmwf",
    "system": "51",
    "variable": ["total_precipitation"],
    "product_type": "monthly_mean",
    "year": ["2025"],
    "month": ["12"],
    "leadtime_month": [
        "1", "2", "3", "4", "5", "6" # Pronóstico a 6 meses
    ],
    "data_format": "netcdf", # Usamos NetCDF para facilitar la conversión a CSV sin cfgrib
    
    "area": [
        -30.0, -65.0, -38.0, -56.0,
    ],
}

client.retrieve(dataset, request).download('pronostico_6m.nc')

print("¡Descarga finalizada! Archivo: pronostico_6m.nc")