
import sys
import os

# Ajustar path para importar 'core'
sys.path.append(os.path.abspath('web_platform'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "climate_viewer.settings")

import django
django.setup()

from core.analysis import load_datasets, get_skill_matrix

print("Iniciando carga de datasets...")
try:
    ds = load_datasets()
    print("Datasets cargados OK.")
    print("Claves:", ds.keys())
    
    print("Calculando matriz...")
    # Usar coords del usuario
    res = get_skill_matrix(-36.578, -59.284, 1)
    print("Resultado parcial:", list(res.keys()))
    
except Exception as e:
    print("\n!!!!!!! ERROR FATAL !!!!!!!")
    print(e)
    import traceback
    traceback.print_exc()
