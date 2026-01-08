
import cdsapi
import os

c = cdsapi.Client()

# Directorio de datos
DATA_DIR = 'data_bsas'
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Modelos disponibles en CDS Seasonal
models = {
    'ecmwf': '51',
    'ukmo': '602',
    'meteo_france': '8',
    'dwd': '21',
    'cmcc': '35',
    'ncep': '2',
    'jma': '3',
    'eccc': '3'
}

# Configuración de la descarga
# Intentamos bajar el último disponible. 
# NOTA: Ajusta AÑO y MES a la fecha actual real si es necesario.
# Asumimos Enero 2026 (o Diciembre 2025 si Ene no salió).
YEAR = '2025' 
MONTH = '12' 

print(f"Iniciando descarga de pronósticos operativos para {YEAR}-{MONTH}...")

for system, origin in models.items():
    filename = os.path.join(DATA_DIR, f'operational_{system}_{YEAR}{MONTH}.nc')
    
    if os.path.exists(filename):
        print(f"Ya existe: {filename}")
        continue
        
    print(f"Descargando {system}...")
    
    try:
        c.retrieve(
            'seasonal-monthly-single-levels',
            {
                'format': 'netcdf', # CAMBIO A NETCDF
                'originating_centre': system,
                'system': origin,
                'variable': 'total_precipitation',
                'product_type': 'monthly_mean',
                'year': YEAR,
                'month': MONTH,
                'leadtime_month': ['1', '2', '3', '4', '5', '6'],
                'area': [
                    -33, -64, -41, -56, 
                ],
            },
            filename)
        print(f"Descargado: {filename}")
    except Exception as e:
        print(f"Error descargando {system}: {e}")

print("¡Proceso finalizado!")
