# test_analysis.py
import os
import sys

# Agregar path para imports
sys.path.append(os.path.abspath('web_platform'))

from core.analysis import get_skill_matrix

print("Probando cálculo para un punto en BA...")
try:
    # Lat/Lon de prueba (centro BA)
    lat = -36.0
    lon = -60.0 # Oeste
    base_month = 1
    
    result = get_skill_matrix(lat, lon, base_month)
    print("Resultado:")
    print(result)
except Exception as e:
    print("ERROR FATAL:")
    import traceback
    traceback.print_exc()
