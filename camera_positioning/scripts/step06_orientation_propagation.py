import json
import math
import numpy as np
import matplotlib.pyplot as plt

def normalize_angle(angle):
    """Normaliza un ángulo a [0, 360)."""
    return angle % 360

def normalize_angle_diff(diff):
    """Normaliza una diferencia angular al rango [-180, 180)."""
    return ((diff + 180) % 360) - 180

def ideal_tangent_angle(cx, cy, x, y):
    """
    Calcula el ángulo ideal de la tangente al círculo definido por (cx,cy) y la posición (x,y).
    """
    dx = x - cx
    dy = y - cy
    angle = math.degrees(math.atan2(dx, -dy))
    return normalize_angle(angle)

def compute_offsets(originals, cx, cy):
    """
    Calcula los offsets de Omega, Phi y Kappa comparando contra la orientación ideal.
    """
    offsets_omega, offsets_phi, offsets_kappa = [], [], []
    for it in originals:
        try:
            x, y = float(it["X"]), float(it["Y"])
            omega, phi, kappa = float(it["Omega"]), float(it["Phi"]), float(it["Kappa"])
        except Exception:
            continue
        ideal_kappa = ideal_tangent_angle(cx, cy, x, y)
        offsets_omega.append(omega)
        offsets_phi.append(phi)
        offsets_kappa.append(normalize_angle_diff(kappa - ideal_kappa))
    return offsets_omega, offsets_phi, offsets_kappa

def apply_offsets(items, cx, cy, median_omega, median_phi, median_kappa):
    """
    Aplica los offsets a las imágenes no originales para obtener la orientación corregida.
    """
    for it in items:
        if it.get("Calibration_Status") in ["visually calibrated", "estimated"]:
            try:
                x, y = float(it["X"]), float(it["Y"])
            except Exception:
                continue
            ideal_kappa = ideal_tangent_angle(cx, cy, x, y)
            it["Omega"] = median_omega
            it["Phi"] = median_phi
            it["Kappa"] = normalize_angle(ideal_kappa + median_kappa)
    return items

def propagate_orientation(json_input_path, json_output_path):
    """
    Corrige la orientación de imágenes no originales basándose en los offsets detectados en originales.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    for step, info in data.items():
        if "axis_center" in info:
            cx, cy = float(info["axis_center"]["x"]), float(info["axis_center"]["y"])
        else:
            print(f"Step {step}: No se encontró axis_center. Se omite.")
            continue
        items = info.get("items", [])
        originals = [it for it in items if it.get("Calibration_Status") == "original"]
        if not originals:
            print(f"Step {step}: No hay originales válidas. Se omite.")
            continue
        offsets_omega, offsets_phi, offsets_kappa = compute_offsets(originals, cx, cy)
        median_omega = np.median(offsets_omega) if offsets_omega else 0.0
        median_phi = np.median(offsets_phi) if offsets_phi else 0.0
        median_kappa = np.median(offsets_kappa) if offsets_kappa else 0.0
        print(f"Step {step}: Offsets medianos -> Omega: {median_omega:.2f}°, Phi: {median_phi:.2f}°, Kappa: {median_kappa:.2f}°")
        apply_offsets(items, cx, cy, median_omega, median_phi, median_kappa)
    
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    print(f"✅ Propagación de orientación completada. Archivo guardado en {json_output_path}")
