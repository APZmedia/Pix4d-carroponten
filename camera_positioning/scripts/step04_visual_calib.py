import json
import pandas as pd
import numpy as np
from processing.angular_transform import angle_to_xy

def calculate_theta(x, y, center_x, center_y):
    """
    Calcula el ángulo Theta basado en la posición (X, Y) respecto al centro.
    Devuelve el ángulo en grados dentro del rango [0, 360].
    """
    theta_rad = np.arctan2(y - center_y, x - center_x)  # Ángulo en radianes
    theta_deg = np.degrees(theta_rad)  # Convertir a grados
    return theta_deg % 360  # Asegurar que el ángulo está en [0, 360]

def calibrate_visually(json_input_path, csv_input_path, json_output_path):
    """
    Calibra imágenes usando información del CSV con posiciones angulares.
    1️⃣ Asigna Theta a las imágenes "original" basado en su (X, Y).
    2️⃣ Asigna Theta a "visually calibrated" usando el CSV.
    3️⃣ Interpola Theta en "estimated" basándose en imágenes calibradas.
    4️⃣ Convierte Theta a (X, Y) para todas las imágenes.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    visual_matches = pd.read_csv(csv_input_path)

    sequence_columns = list(visual_matches.columns[1:-1])  # Todas las secuencias menos "LandmarkID" y "Theta"
    angle_column = "Theta"

    # 📌 Paso 1: Calcular Theta para "original" usando (X, Y)
    for step_name, step_info in sequences_data.items():
        if "axis_center" not in step_info:
            continue  # Saltamos secuencias sin centro definido

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]

        for item in step_info.get("items", []):
            if item.get("Calibration_Status") == "original":
                x, y = item.get("X"), item.get("Y")

                if x is not None and y is not None:
                    item["Angular position"] = calculate_theta(x, y, center_x, center_y)

    # 📌 Paso 2: Asignar Theta a "visually calibrated" desde el CSV
    for step_name, step_info in sequences_data.items():
        if step_name not in sequence_columns:
            continue

        for item in step_info.get("items", []):
            if item.get("Calibration_Status") == "visually calibrated":
                filename = item.get("Filename", "").strip()
                match = visual_matches[visual_matches["LandmarkID"] == filename]

                if not match.empty:
                    item["Angular position"] = float(match[angle_column].values[0])

    # 📌 Paso 3: Interpolar Theta para "estimated"
    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        calibrated_indices = [i for i, item in enumerate(items) if item.get("Calibration_Status") in ["original", "visually calibrated"]]
        estimated_indices = [i for i, item in enumerate(items) if item.get("Calibration_Status") == "estimated"]

        for idx in estimated_indices:
            prev_idx = max([i for i in calibrated_indices if i < idx], default=None)
            next_idx = min([i for i in calibrated_indices if i > idx], default=None)

            if prev_idx is not None and next_idx is not None:
                prev_theta = items[prev_idx]["Angular position"]
                next_theta = items[next_idx]["Angular position"]
                factor = (idx - prev_idx) / (next_idx - prev_idx)
                items[idx]["Angular position"] = prev_theta + factor * (next_theta - prev_theta)

    # 📌 Paso 4: Convertir Theta a coordenadas (X, Y)
    for step_name, step_info in sequences_data.items():
        if "axis_center" not in step_info or "calculated_radius" not in step_info:
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]

        for item in step_info.get("items", []):
            if "Angular position" in item:
                theta = item["Angular position"]
                x, y, _ = angle_to_xy(theta, radius)

                item["X"] = x
                item["Y"] = y

    # 📌 Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Calibración visual completada. JSON guardado en {json_output_path}")
