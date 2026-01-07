
import xarray as xr
import pandas as pd
import os

def check_jma():
    f = 'data_bsas/hc_jma_3_bsas.nc'
    if not os.path.exists(f): return "No existe JMA"
    
    ds = xr.open_dataset(f)
    print("JM Vars:", list(ds.data_vars))
    
    # 1. Normalizar
    ds = ds.rename({'forecastMonth': 'lead', 'tprate': 'tp'})
    if 'number' in ds.dims: ds = ds.mean(dim='number')
    
    # 2. Seleccionar punto
    lat, lon = -34.6, -58.4
    point = ds['tp'].sel(latitude=lat, longitude=lon, method='nearest')
    
    # 3. Dataframe
    df = point.to_dataframe().reset_index()
    print("Columnas:", df.columns)
    
    # 4. Check Meses
    coords = [c for c in df.columns if 'time' in c or 'date' in c]
    print("Coords tiempo:", coords)
    
    col_date = 'time' # JMA usa 'time' como start date
    df['mes'] = df[col_date].dt.month
    print("Meses unicos:", df['mes'].unique())
    
    # 5. Check Enero
    enero = df[df['mes'] == 1]
    print(f"Filas Enero: {len(enero)}")
    if not enero.empty:
        print("Muestra Enero:", enero.head())

if __name__ == "__main__":
    check_jma()
