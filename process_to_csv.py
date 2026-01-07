import xarray as xr
import pandas as pd
import numpy as np
import calendar

file_path = 'pronostico_6m.nc'
output_csv = 'pronostico_procesado.csv'

# Open dataset
ds = xr.open_dataset(file_path)

# 1. Calcular promedio del ensamble (dimension 'number')
if 'number' in ds.dims:
    print("Calculando media del ensamble (51 miembros)...")
    ds = ds.mean(dim='number')

# 2. Identificar variable (tprate)
var_name = 'tprate'
if var_name not in ds:
    var_name = list(ds.data_vars)[0]
print(f"Variable de datos: {var_name}")

# 3. Convertir a DataFrame
df = ds.to_dataframe().reset_index()
print("Columnas encontradas:", df.columns.tolist())

# 4. Mapeo de columnas basado en lo que vimos en info.txt
# Coordinates: forecastMonth, forecast_reference_time, latitude, longitude
col_map = {
    'latitude': 'lat',
    'longitude': 'lon',
    'forecast_reference_time': 'fecha_actual',
    'forecastMonth': 'mes_pronostico'
}

df.rename(columns=col_map, inplace=True)
print("Columnas renombradas:", df.columns.tolist())

# Validar columnas necesarias
required = ['lat', 'lon', 'fecha_actual', 'mes_pronostico', var_name]
missing = [c for c in required if c not in df.columns]
if missing:
    print(f"Error: Faltan columnas: {missing}")
    exit(1)

# 5. Conversión de unidades
# tprate (m/s) -> mm/mes
def convert_rate_to_mm(row):
    start_date = row['fecha_actual']
    lead = int(row['mes_pronostico'])
    
    # Calcular fecha del mes objetivo
    target_date = start_date + pd.DateOffset(months=lead)
    days_in_month = target_date.days_in_month
    
    val = row[var_name]
    # m/s * 86400 s/d * days * 1000 mm/m
    mm = val * 86400 * days_in_month * 1000
    return mm

print("Convirtiendo unidades (m/s -> mm/mes)...")
df['valor'] = df.apply(convert_rate_to_mm, axis=1)

# 6. Formato final
# lat, lon, fecha_actual, mes_pronostico, variable, valor
final_df = df[['lat', 'lon', 'fecha_actual', 'mes_pronostico', 'valor']].copy()
final_df['variable'] = 'precipitacion_acumulada'
final_df['valor'] = final_df['valor'].round(2)

# Ordenar para que quede prolijo
final_df.sort_values(by=['lat', 'lon', 'mes_pronostico'], inplace=True)

# Guardar
final_df.to_csv(output_csv, index=False)
print(f"¡CSV generado exitosamente! -> {output_csv}")
print(final_df.head(10))
