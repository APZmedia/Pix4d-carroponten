import json
import numpy as np
from scipy.optimize import least_squares

def fit_circle(x, y):
    """
    Ajusta un círculo a un conjunto de puntos usando mínimos cuadrados.
    Retorna el centro (Xc, Yc) y el radio.
    """
    def residuals(params, x, y):
        xc, yc, r = params
        return np.sqrt((x - xc) ** 2 + (y - yc) ** 2) - r

    x_m, y_m = np.mean(x), np.mean(y)
    r_initial = np.mean(np.sqrt((x - x_m) ** 2 + (y - y_m) ** 2))

    res = least_squares(residuals, x0=[x_m, y_m, r_initial], args=(x, y))
    return res.x  # Devuelve xc, yc, r

def estimate_center_and_radius(json_input_path, json_output_path):
    """
    Determina el mejor centro basado en la secuencia con más imágenes calibradas
    y propaga ese centro a todas las secuencias.
    Luego, calcula el radio de cada secuencia como la distancia promedio a ese centro.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    # 📌 Paso 1: Determinar la secuencia con más imágenes calibradas
    best_sequence = None
    best_x_cal, best_y_cal = [], []

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        x_cal, y_cal = [], []
        for item in items:
            if item.get("Calibration_Status") == "calibrated" and "X" in item and "Y" in item:
                x_cal.append(item["X"])
                y_cal.append(item["Y"])

        if len(x_cal) > len(best_x_cal):  # Buscamos la secuencia con más calibradas
            best_x_cal, best_y_cal = x_cal, y_cal
            best_sequence = step_name

    if len(best_x_cal) < 3:
        print("❌ No hay suficientes imágenes calibradas en ninguna secuencia para calcular el centro.")
        return

    # 📌 Paso 2: Calcular el mejor centro
    best_xc, best_yc, _ = fit_circle(np.array(best_x_cal), np.array(best_y_cal))
    print(f"✅ Mejor centro basado en {best_sequence}: ({best_xc:.3f}, {best_yc:.3f})")

    # 📌 Paso 3: Propagar el centro a todas las secuencias y calcular radios
    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        x_cal, y_cal = [], []
        for item in items:
            if item.get("Calibration_Status") == "calibrated":
                x_cal.append(item["X"])
                y_cal.append(item["Y"])

        if len(x_cal) < 3:
            print(f"⚠️ No hay suficientes imágenes calibradas en {step_name} para calcular un radio.")
            continue

        # 📌 Calcular el radio usando la distancia promedio al mejor centro
        distances = np.sqrt((np.array(x_cal) - best_xc) ** 2 + (np.array(y_cal) - best_yc) ** 2)
        avg_radius = np.mean(distances)

        # 📌 Guardar en el JSON
        step_info["axis_center"] = {"x": best_xc, "y": best_yc}
        step_info["calculated_radius"] = avg_radius
        print(f"✅ {step_name}: Centro ({best_xc:.3f}, {best_yc:.3f}), Radio {avg_radius:.3f}")

    # 📌 Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Centros propagados y radios calculados en: {json_output_path}")
