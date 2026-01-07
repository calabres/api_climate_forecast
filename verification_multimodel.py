import cdsapi
import xarray as xr
import pandas as pd
import numpy as np
import os
from scipy.stats import pearsonr

# --- CONFIGURACIÓN ---
LAT = -35.5
LON = -60.0
AREA = [LAT+0.1, LON-0.1, LAT-0.1, LON+0.1]

# Periodo Hindcast Estándar
YEARS_HINDCAST = [str(y) for y in range(1993, 2017)] 
# ERA5 cubre lo mismo + margen
YEARS_ERA5 = [str(y) for y in range(1993, 2018)]    

client = cdsapi.Client()

# Diccionario de Modelos y sus System IDs (suelen ser estables, pero pueden requerir updates)
# Nota: Algunos pueden fallar si cambiaron versiones recientemente en CDS, manejaremos errores.
MODELS = {
    'ecmwf': '51',
    'ukmo': '602',
    'meteo_france': '8',
    'dwd': '21',
    'cmcc': '35',
    'ncep': '2',
    'jma': '3',
    'eccc': '3', 
    # 'bom': '5' # BOM a veces tiene acceso restringido o problemas de API. Lo dejamos fuera por seguridad inicial.
}

def download_era5():
    filename = 'obs_era5_1993_2017.nc'
    if os.path.exists(filename):
        return filename
    
    print(f"--> Descargando ERA5 (Observación Ref)...")
    client.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'format': 'netcdf',
            'product_type': 'monthly_averaged_reanalysis',
            'variable': 'total_precipitation',
            'year': YEARS_ERA5,
            'month': [str(i).zfill(2) for i in range(1, 13)],
            'time': '00:00',
            'area': AREA,
        },
        filename
    )
    return filename

def download_hindcast(center, system):
    filename = f'hc_{center}_1993_2016.nc'
    if os.path.exists(filename):
        return filename
    
    print(f"--> Descargando Hindcast {center} (System {system})...")
    try:
        client.retrieve(
            'seasonal-monthly-single-levels',
            {
                'format': 'netcdf',
                'originating_centre': center,
                'system': system,
                'variable': 'total_precipitation',
                'product_type': 'monthly_mean',
                'year': YEARS_HINDCAST,
                'month': [str(i).zfill(2) for i in range(1, 13)],
                'leadtime_month': ['1','2','3','4','5','6'],
                'area': AREA,
            },
            filename
        )
        return filename
    except Exception as e:
        print(f" X Error descargando {center}: {e}")
        return None

def process_model(model_name, hc_file, obs_ts):
    print(f"   Procesando {model_name}...")
    ds_hc = xr.open_dataset(hc_file)
    
    # Media ensamble
    if 'number' in ds_hc.dims: ds_hc = ds_hc.mean(dim='number')
    
    # Punto mas cercano
    ds_point = ds_hc.sel(latitude=LAT, longitude=LON, method='nearest')
    
    results = []
    
    # Matriz 12 meses x 6 leads
    for start_month in range(1, 13):
        for lead in range(1, 7):
            preds = []
            obs = []
            
            for year in range(1993, 2017):
                # Fecha Forecast
                try:
                    start_date = pd.Timestamp(year, start_month, 1)
                except: continue
                
                # Valor Pronosticado
                try:
                    # tprate en m/s
                    val_pred_rate = ds_point['tprate'].sel(
                        forecast_reference_time=start_date, 
                        forecastMonth=lead
                    ).item()
                except KeyError: continue
                
                # Conversión a mm (Pronostico)
                target_date = start_date + pd.DateOffset(months=lead)
                days = target_date.days_in_month
                val_pred_mm = val_pred_rate * 86400 * days * 1000
                
                # Valor Observado (ERA5 ya en mm? NO, ERA5 tp is "m". A veces "Total precipitation" en monthly means es tasa media?)
                # ERA5 monthly averaged dataset: unit 'm'. It is accumulated or mean rate?
                # Documentación dice: "Monthly mean of daily forecast accumulations" -> m/day? No.
                # Usually ERA5 monthly is 'm/day' or 'm' accumulated.
                # TRICK: Para correlation (ACC) NO importa la unidad. Para BIAS sí.
                # Asumiremos la conversion m -> mm.
                
                target_str = target_date.strftime('%Y-%m-01')
                try:
                    # ERA5 tp is in METERS in CDS monthly means.
                    val_obs_m = obs_ts[target_str]
                    val_obs_mm = val_obs_m * 1000 
                except KeyError: continue
                
                if not np.isnan(val_pred_mm) and not np.isnan(val_obs_mm):
                    preds.append(val_pred_mm)
                    obs.append(val_obs_mm)
            
            # Métricas
            if len(preds) > 15:
                # ACC (Correlation)
                corr, _ = pearsonr(preds, obs)
                # BIAS (Mean Error)
                bias = np.mean(preds) - np.mean(obs)
            else:
                corr = np.nan
                bias = np.nan
            
            results.append({
                'model': model_name,
                'mes_inicio': start_month,
                'lead_time': lead,
                'acc': round(corr, 3),   # Anomaly Correlation Coefficient
                'bias': round(bias, 1),  # Bias en mm
                'n': len(preds)
            })
            
    return results

def main():
    # 1. Observación
    file_era5 = download_era5()
    
    # Preparar serie obs en memoria
    ds_obs = xr.open_dataset(file_era5)
    ts_obs = ds_obs['tp'].sel(latitude=LAT, longitude=LON, method='nearest').to_dataframe()['tp']
    
    all_results = []
    
    # 2. Bucle Modelos
    for name, sys_id in MODELS.items():
        print(f"\n--- Evaluando {name.upper()} ---")
        file_hc = download_hindcast(name, sys_id)
        
        if file_hc:
            res = process_model(name, file_hc, ts_obs)
            all_results.extend(res)
            
    # 3. Guardar Final
    if all_results:
        df = pd.DataFrame(all_results)
        df.to_csv('validacion_multimodelo_1993_2016.csv', index=False)
        print("\n\n proceso Terminado!")
        print("Resultados guardados en: validacion_multimodelo_1993_2016.csv")
        
        # Mostrar pequeño resumen: Mejor modelo promedio por Lead Time
        print("\n--- MEJOR MODELO POR LEAD TIME (Promedio ACC todos los meses) ---")
        mejores = df.groupby(['lead_time', 'model'])['acc'].mean().unstack()
        print(mejores)
    else:
        print("No se obtuvieron resultados.")

if __name__ == "__main__":
    main()
