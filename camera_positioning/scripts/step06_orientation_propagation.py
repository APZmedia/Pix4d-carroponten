import json
import numpy as np
import pandas as pd
from scipy.signal import savgol_filter
from processing.coordinate_conversion import opk_to_ypr, ypr_to_opk

def fit_sinusoidal_trend(angular_positions, values):
    """
    Ajusta un modelo sinusoidal a los datos de orientación dentro de cada secuencia.
    """
    if len(angular_positions) < 3:
        return lambda x: np.mean(values)  # Retorna la media si hay pocos datos
    
    from scipy.optimize import curve_fit
    
    def sinusoidal(x, A, B, C, D):
        return A * np.sin(B * x + C) + D
    
    try:
        params, _ = curve_fit(sinusoidal, angular_positions, values, 
                               p0=[np.std(values), 2 * np.pi / (max(angular_positions) - min(angular_positions) + 1), 0, np.mean(values)],
                               maxfev=5000)
        return lambda x: sinusoidal(x, *params)
    except RuntimeError:
        print("⚠️ Advertencia: No se pudo ajustar la curva sinusoidal, se usará la media como fallback.")
        return lambda x: np.mean(values)

def compute_sinusoidal_offsets(sequence_items):
    """
    Calcula la tendencia sinusoidal para Omega y Phi y una tendencia lineal para Kappa dentro de cada secuencia.
    """
    if len(sequence_items) < 3:
        return None
    
    angular_positions = np.array([item["Angular position"] for item in sequence_items])
    omega_values = np.array([item["Omega"] for item in sequence_items])
    phi_values = np.array([item["Phi"] for item in sequence_items])
    kappa_values = np.array([item["Kappa"] for item in sequence_items])
    
    # Aplicar suavizado Savitzky-Golay
    window_size = min(11, len(angular_positions)) if len(angular_positions) > 3 else len(angular_positions)
    poly_order = 3 if window_size > 3 else 1
    
    omega_values_smooth = savgol_filter(omega_values, window_size, poly_order)
    phi_values_smooth = savgol_filter(phi_values, window_size, poly_order)
    kappa_values_smooth = savgol_filter(kappa_values, window_size, poly_order)
    
    omega_trend = fit_sinusoidal_trend(angular_positions, omega_values_smooth)
    phi_trend = fit_sinusoidal_trend(angular_positions, phi_values_smooth)
    kappa_slope, kappa_intercept = np.polyfit(angular_positions, kappa_values_smooth, 1)
    
    return omega_trend, phi_trend, lambda x: kappa_slope * x + kappa_intercept

def apply_orientation_correction(sequence_items, omega_trend, phi_trend, kappa_trend):
    """
    Aplica la corrección basada en la posición angular dentro de la secuencia.
    """
    for item in sequence_items:
        if item.get("Calibration_Status") in ["visually calibrated", "estimated"]:
            x = item["Angular position"]
            item["Omega"] = omega_trend(x)
            item["Phi"] = phi_trend(x)
            item["Kappa"] = kappa_trend(x)

def propagate_orientation(json_input_path, json_output_path):
    """
    Corrige la orientación de imágenes no originales usando ajustes sinusoidales y lineales dentro de cada secuencia.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for step, info in data.items():
        items = info.get("items", [])
        sequences = {}
        
        # Agrupar por secuencia
        for item in items:
            seq_id = item.get("Sequence", "Unknown")
            if seq_id not in sequences:
                sequences[seq_id] = []
            sequences[seq_id].append(item)
        
        # Procesar cada secuencia individualmente
        for seq_id, sequence_items in sequences.items():
            originals = [it for it in sequence_items if it.get("Calibration_Status") == "original"]
            if len(originals) < 3:
                continue
            
            omega_trend, phi_trend, kappa_trend = compute_sinusoidal_offsets(originals)
            apply_orientation_correction(sequence_items, omega_trend, phi_trend, kappa_trend)
    
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Propagación de orientación completada por secuencia con suavizado. Archivo guardado en {json_output_path}")