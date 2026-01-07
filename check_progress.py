
import os
import glob
import time

def check_status():
    data_dir = 'data_bsas'
    files = glob.glob(os.path.join(data_dir, '*.nc'))
    
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

    found = []
    print("\n" + "="*40)
    print(f" ESTADO DE DESCARGAS ({time.strftime('%H:%M:%S')})")
    print("="*40)
    
    for f in files:
        name = os.path.basename(f)
        for k in models_map:
            if k in name: found.append(k)

    count = 0
    for k, label in models_map.items():
        if k in found:
            print(f"✅ {label}")
            count += 1
        else:
            print(f"⏳ {label}...")
            
    print("-" * 40)
    print(f"Progreso: {count}/{len(models_map)} modelos listos.")
    print("="*40 + "\n")

if __name__ == "__main__":
    check_status()
