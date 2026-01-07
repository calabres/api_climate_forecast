import cdsapi
import os

# --- CONFIGURACIÓN ZONA BUENOS AIRES ---
# Norte, Oeste, Sur, Este
AREA_BSAS = [-33.0, -64.0, -42.0, -56.5]

YEARS = [str(y) for y in range(1993, 2017)] 

client = cdsapi.Client()

MODELS = {
    'era5': 'reanalysis-era5-single-levels-monthly-means', # Reference
    'ecmwf': '51',
    'ukmo': '602',
    'meteo_france': '8',
    'dwd': '21',
    'cmcc': '35',
    'ncep': '2',
    'jma': '3',
    'eccc': '3',
}

def main():
    if not os.path.exists("data_bsas"):
        os.makedirs("data_bsas")
        
    print(f"--- INICIANDO DESCARGA MASIVA PARA BUENOS AIRES ---")
    print(f"Zona: {AREA_BSAS}")
    print(f"Periodo: 1993-2016")

    # 1. Descargar ERA5 (Observación)
    file_era5 = "data_bsas/era5_obs_bsas_1993_2016.nc"
    if not os.path.exists(file_era5):
        print("\n--> Descargando ERA5 (Observación)...")
        try:
            client.retrieve(
                'reanalysis-era5-single-levels-monthly-means',
                {
                    'format': 'netcdf',
                    'product_type': 'monthly_averaged_reanalysis',
                    'variable': 'total_precipitation',
                    'year': YEARS,
                    'month': [str(i).zfill(2) for i in range(1, 13)],
                    'time': '00:00',
                    'area': AREA_BSAS,
                },
                file_era5
            )
            print("    OK ERA5")
        except Exception as e:
            print(f"    Error ERA5: {e}")
    else:
        print("\n--> ERA5 ya existe, saltando.")

    # 2. Descargar Hindcasts (Modelos)
    for name, sys_id in MODELS.items():
        if name == 'era5': continue # Ya procesado
        
        file_hc = f"data_bsas/hc_{name}_{sys_id}_bsas.nc"
        if os.path.exists(file_hc):
            print(f"--> {name.upper()} ya existe, saltando.")
            continue
            
        print(f"\n--> Descargando Hindcast {name.upper()}...")
        try:
            client.retrieve(
                'seasonal-monthly-single-levels',
                {
                    'format': 'netcdf',
                    'originating_centre': name,
                    'system': sys_id,
                    'variable': 'total_precipitation',
                    'product_type': 'monthly_mean',
                    'year': YEARS,
                    'month': [str(i).zfill(2) for i in range(1, 13)],
                    'leadtime_month': ['1','2','3','4','5','6'],
                    'area': AREA_BSAS,
                },
                file_hc
            )
            print(f"    OK {name.upper()}")
        except Exception as e:
            print(f"    Error {name}: {e}")

if __name__ == "__main__":
    main()
