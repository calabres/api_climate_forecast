
import xarray as xr
import os

files = {
    'JMA': 'hc_jma_3_bsas.nc',
    'NCEP': 'hc_ncep_2_bsas.nc',
    'UKMO': 'hc_ukmo_602_bsas.nc'
}

data_dir = 'data_bsas'

for name, fname in files.items():
    path = os.path.join(data_dir, fname)
    if os.path.exists(path):
        print(f"\n--- {name} ({fname}) ---")
        try:
            ds = xr.open_dataset(path)
            print("Dims:", list(ds.dims))
            print("Coords:", list(ds.coords))
            print("Data Vars:", list(ds.data_vars))
            
            # Print first few coordinate values to understand structure
            for c in ds.coords:
                print(f"  {c}: {ds[c].values[:2]} ...")
                
        except Exception as e:
            print(f"Error reading: {e}")
    else:
        print(f"File not found: {fname}")
