
import xarray as xr
import pandas as pd
import numpy as np
import os
import glob
from scipy.stats import pearsonr
from calendar import monthrange
import re
import traceback
import threading

# Ruta de datos
DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../data_bsas'))

# Lock global para evitar que dos hilos abran archivos NetCDF al mismo tiempo
file_lock = threading.Lock()

def get_latest_op_date():
    op_files = glob.glob(os.path.join(DATA_DIR, 'operational_*.nc'))
    max_date = 0
    if not op_files: return None, None
    for f in op_files:
        match = re.search(r'_(\d{6})\.nc', f)
        if match:
             d = int(match.group(1))
             if d > max_date: max_date = d
    if max_date == 0: return None, None
    return str(max_date)[:4], str(max_date)[4:]

def get_skill_matrix(lat, lon, base_month):
    print(f"--- Iniciando análisis de Skill para {lat}, {lon} (Mes {base_month}) ---")
    
    with file_lock:
        # Si base_month es None o 'auto', usar el último disponible
        if not base_month or base_month == 'auto':
            _, op_m = get_latest_op_date()
            base_month = int(op_m) if op_m else 1 # Default Enero simulado
    
        response_acc = {}
        response_bias = {}
        
        # 1. Cargar Observaciones (ERA5)
        ts_obs = None
        era5_path = os.path.join(DATA_DIR, 'era5_obs_bsas_1993_2016.nc')
        
        if not os.path.exists(era5_path):
            return {"error": "Falta archivo ERA5"}
            
        try:
            # Abrimos sin lock=False para evitar que colisionen pedidos simultáneos
            with xr.open_dataset(era5_path, engine='netcdf4') as ds_obs:
                var_name = 'tp' if 'tp' in ds_obs else list(ds_obs.data_vars)[0]
                # Extraer punto exacto y cargarlo en RAM
                point_obs = ds_obs[var_name].sel(latitude=lat, longitude=lon, method='nearest').load()
                ts_obs = point_obs.to_dataframe()[point_obs.name]
                print(f"ERA5 cargado OK")
        except Exception as e:
            print(f"Error crítico leyendo ERA5: {e}")
            return {"error": f"Error leyendo ERA5: {e}"}
    
        # 2. Iterar sobre todos los modelos
        model_files = sorted(glob.glob(os.path.join(DATA_DIR, 'hc_*_bsas.nc')))
        
        for f in model_files:
            name_parts = os.path.basename(f).split('_')
            if len(name_parts) < 2: continue
            model_name = name_parts[1]
            
            try:
                with xr.open_dataset(f, engine='netcdf4') as ds:
                    # Normalización On-The-Fly
                    if 'number' in ds.dims: ds = ds.mean(dim='number')
                    
                    for v in ['tprate', 'total_precipitation', 'precip', 'precipitation_flux']:
                        if v in ds: ds = ds.rename({v: 'tp'})
                    
                    if 'tp' not in ds:
                         print(f"Modelo {model_name} no tiene variable 'tp'")
                         response_acc[model_name] = [None]*6
                         response_bias[model_name] = [None]*6
                         continue
                         
                    point_val = ds['tp'].sel(latitude=lat, longitude=lon, method='nearest').compute()
                    df_mod = point_val.to_dataframe().reset_index()
                    
                    col_lead = None
                    for c in ['lead', 'forecastMonth', 'leadtime_month', 'step']:
                        if c in df_mod.columns:
                            col_lead = c
                            break
                    
                    col_date = None
                    for c in ['start_date', 'time', 'forecast_reference_time', 'indexing_time', 'index']:
                        if c in df_mod.columns and pd.api.types.is_datetime64_any_dtype(df_mod[c]):
                            col_date = c
                            break
                                
                    if not col_lead or not col_date:
                        print(f"Modelo {model_name} tiene columnas incompatibles")
                        response_acc[model_name] = [None]*6
                        response_bias[model_name] = [None]*6
                        continue
    
                    # Filtrar mes base
                    df_mod['base_month_idx'] = df_mod[col_date].dt.month
                    df_filtered = df_mod[df_mod['base_month_idx'] == int(base_month)]
                    
                    if df_filtered.empty:
                        response_acc[model_name] = [None]*6
                        response_bias[model_name] = [None]*6
                        continue
                    
                    # Calcular correlaciones y bias
                    scores_acc = []
                    scores_bias = []
                    
                    for lead in range(1, 7):
                        lead_data = df_filtered[df_filtered[col_lead] == lead]
                        if lead_data.empty:
                            scores_acc.append(None)
                            scores_bias.append(None)
                            continue
                            
                        preds_mm = []
                        obs_mm = []
                        
                        for _, row in lead_data.iterrows():
                            dt_ref = row[col_date]
                            year = dt_ref.year
                            target_m = (int(base_month) - 1 + lead)%12 + 1
                            target_y = year if (int(base_month) - 1 + lead) < 12 else year + 1
                            
                            try:
                                # Buscar en OBS (ERA5) de forma vectorizada/eficiente
                                target_date = pd.Timestamp(f"{target_y}-{target_m:02d}-01")
                                
                                # Intentar acceso directo por índice si es posible (más rápido)
                                if target_date in ts_obs.index:
                                    val_obs = ts_obs.loc[target_date]
                                else:
                                    start_w = target_date - pd.Timedelta(days=5)
                                    end_w = target_date + pd.Timedelta(days=35)
                                    subset_obs = ts_obs[start_w:end_w]
                                    subset_obs = subset_obs[(subset_obs.index.month == target_m) & (subset_obs.index.year == target_y)]
                                    if subset_obs.empty: continue
                                    val_obs = float(subset_obs.values[0])
                                    
                                val_pred = float(row['tp'])
                                
                                # OBSERVACION (ERA5)
                                val_obs_mm = val_obs * 1000
                                _, d_in_m = monthrange(target_y, target_m)
                                if val_obs_mm < 20: 
                                    val_obs_mm *= d_in_m
    
                                # PREDICCION (Modelos)
                                if abs(val_pred) < 0.01:
                                    secs_in_month = d_in_m * 24 * 3600
                                    val_pred_mm = val_pred * secs_in_month * 1000
                                else:
                                    val_pred_mm = val_pred * 1000
                                
                                preds_mm.append(val_pred_mm)
                                obs_mm.append(val_obs_mm)
                            except: pass
                        
                        if len(preds_mm) > 10:
                            r, _ = pearsonr(preds_mm, obs_mm)
                            bias = np.mean(preds_mm) - np.mean(obs_mm)
                            obs_stats = np.percentile(obs_mm, [20, 50, 80])
                            
                            scores_acc.append({
                                "r": float(r) if not np.isnan(r) else 0.0,
                                "bias": float(bias),
                                "p20": float(obs_stats[0]),
                                "p50": float(obs_stats[1]),
                                "p80": float(obs_stats[2]),
                                "mean_obs": float(np.mean(obs_mm))
                            })
                            scores_bias.append(float(bias))
                        else:
                            scores_acc.append(None)
                            scores_bias.append(None)
                            
                    response_acc[model_name] = scores_acc
                    response_bias[model_name] = scores_bias
                    print(f"Modelo {model_name} procesado OK")
                    
            except Exception as e:
                print(f"Error procesando {model_name}: {e}")
                response_acc[model_name] = [None]*6
                response_bias[model_name] = [None]*6
    
        print(f"--- Análisis finalizado para {lat}, {lon} ---")
        return {"acc": response_acc, "bias": response_bias, "base_month": int(base_month)}

def get_best_models(lat, lon, base_month_ingored):
    
    OP_YEAR, OP_MONTH = get_latest_op_date()
    if not OP_YEAR: return []
    
    data = get_skill_matrix(lat, lon, int(OP_MONTH))
    if "error" in data: return []
    
    matrix_acc = data["acc"]
    
    champions = []
    start_m = int(OP_MONTH)
    
    months_names = ["", "Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    model_names = list(matrix_acc.keys())
    
    for lead in range(1, 7):
        target_m_idx = (start_m + lead - 1) % 12 + 1
        target_y = int(OP_YEAR) + (1 if (start_m + lead > 12) else 0)
        
        month_label = f"{months_names[target_m_idx]} {str(target_y)[2:]}"
        # 1. Ranking de candidatos
        candidates = []
        for m in model_names:
            acc_list = matrix_acc.get(m, [])
            if len(acc_list) >= lead and acc_list[lead-1] is not None:
                stats = acc_list[lead-1]
                if isinstance(stats, dict):
                    candidates.append((stats['r'], m, stats))
        
        # Ordenar por skill descendente
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        real_forecast_mm = None
        best_model_used = "N/A"
        winner_stats = {"bias": 0, "p20": 0, "p50": 0, "p80": 0, "mean_obs": 0}
        skill_used = 0.0

        # 2. Buscar el mejor disponible
        for acc, m_name, stats in candidates:
             op_file = os.path.join(DATA_DIR, f'operational_{m_name.lower()}_{OP_YEAR}{OP_MONTH}.nc')
             
             if os.path.exists(op_file):
                 try:
                    print(f"Buscando pronóstico operativo: {m_name}...")
                    with xr.open_dataset(op_file, engine='netcdf4') as ds_op:
                        if 'number' in ds_op.dims or 'number' in ds_op.coords:
                            ds_op = ds_op.mean(dim='number', keep_attrs=True)

                        var_op = 'tp' if 'tp' in ds_op else ('tprate' if 'tprate' in ds_op else list(ds_op.data_vars)[0])
                        val_point = ds_op[var_op].sel(latitude=lat, longitude=lon, method='nearest')
                        
                        if 'leadtime_month' in val_point.coords:
                            val_final = val_point.sel(leadtime_month=lead).compute()
                        elif 'forecastMonth' in val_point.coords:
                            val_final = val_point.sel(forecastMonth=lead).compute()
                        elif 'step' in val_point.coords:
                             val_final = val_point.isel(step=lead-1).compute()
                        else:
                            val_final = val_point.compute()
                            
                        val_real = float(val_final.values)
                        
                        _, d_in_m_op = monthrange(target_y, target_m_idx)
                        
                        if abs(val_real) < 0.0001: 
                             real_forecast_mm = val_real * d_in_m_op * 24 * 3600 * 1000
                        elif abs(val_real) < 0.5: 
                             if abs(val_real) < 0.02:
                                 real_forecast_mm = val_real * 1000 * d_in_m_op 
                             else:
                                 real_forecast_mm = val_real * 1000 
                        else:
                             real_forecast_mm = val_real
                             
                    # Si llegamos aca, tenemos dato!
                    best_model_used = m_name
                    winner_stats = stats
                    skill_used = acc
                    break 
                 except Exception as e:
                     print(f"Error reading {m_name}: {e}")
                     continue

        best_model = best_model_used
        best_acc = skill_used

        if real_forecast_mm is None:
             calibrated_forecast = None
             anomalia = None
        else:
             calibrated_forecast = real_forecast_mm - winner_stats['bias']
             anomalia = calibrated_forecast - winner_stats.get('p50', winner_stats['mean_obs'])

        champions.append({
            "lead": lead,
            "mes": month_label,
            "mejor_modelo": best_model.upper(),
            "skill": best_acc,
            "bias": winner_stats['bias'],
            "acumulado_mm": round(calibrated_forecast, 1) if calibrated_forecast is not None else None,
            "anomalia_mm": round(anomalia, 1) if anomalia is not None else None,
            "p20": round(winner_stats['p20'], 1),
            "p50": round(winner_stats.get('p50', 0), 1),
            "p80": round(winner_stats['p80'], 1),
            "confianza": "Alta" if best_acc > 0.5 else ("Media" if best_acc > 0.3 else "Baja")
        })
        
    return champions
