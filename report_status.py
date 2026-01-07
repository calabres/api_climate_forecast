
import os
import glob

data_dir = 'data_bsas'
files = glob.glob(os.path.join(data_dir, '*.nc'))

print("--- REPORTE DE DESCARGAS ---")
found_models = []
models_map = {
    'era5': 'Observaciones (ERA5)',
    'ecmwf': 'ECMWF (Europa)',
    'ukmo': 'UKMO (Reino Unido)',
    'meteo': 'Météo-France (Francia)',
    'dwd': 'DWD (Alemania)',
    'cmcc': 'CMCC (Italia)',
    'ncep': 'NCEP (USA)',
    'jma': 'JMA (Japón)',
    'eccc': 'ECCC (Canadá)'
}

for f in files:
    name = os.path.basename(f)
    size_mb = os.path.getsize(f) / (1024*1024)
    print(f"- {name:<30} | {size_mb:.1f} MB")
    
    for key in models_map:
        if key in name:
            found_models.append(key)

print("\n--- ESTADO ---")
for key, label in models_map.items():
    status = "✅ LISTO" if key in found_models else "⏳ PENDIENTE"
    print(f"{label:<25} : {status}")
