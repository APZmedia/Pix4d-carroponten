import json
import pandas as pd
import numpy as np
from processing.angular_transform import angle_to_xy

def calculate_theta(x, y, center_x, center_y):
    """
    Calcula el ángulo Theta basado en la posición (X, Y) respecto al centro.
    Devuelve el ángulo en grados dentro del rango [-180, 180].
    """
    if x is None or y is None:
        return None  # No calcular si no hay valores válidos

    theta_rad = np.arctan2(y - center_y, x - center_x)  # Ángulo en radianes
    theta_deg = np.degrees(theta_rad)  # Convertir a grados
    return theta_deg  # Mantener en [-180, 180]

def calibrate_visually(json_input_path, csv_input_path, json_output_path):
    """
    Calibra imágenes no calibradas usando información del CSV con posiciones angulares.
    1️⃣ Asigna Theta a "original" usando (X, Y).
    2️⃣ Asigna Theta a "visually calibrated" desde el CSV.
    3️⃣ NO modifica imágenes "uncalibrated".
    4️⃣ Asigna X, Y, Z a "visually calibrated" usando Theta y el radio.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    visual_matches = pd.read_csv(csv_input_path)

    sequence_columns = list(visual_matches.columns[1:-1])  # Todas las secuencias menos "LandmarkID" y "Theta"
    angle_column = "Theta"

    print("\n📌 Iniciando Step 04: Verificación de Theta en imágenes 'original'")

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
                    print(f"🟠 {item.get('Filename', 'Unknown')}: Theta calculado = {item['Angular position']}°")
                else:
                    print(f"⚠️ {item.get('Filename', 'Unknown')}: No tiene X, Y para calcular Theta.")

    print("\n📌 Verificación de Theta en imágenes 'visually calibrated'")

    # 📌 Paso 2: Asignar Theta a "visually calibrated" desde el CSV
    for step_name, step_info in sequences_data.items():
        if step_name not in sequence_columns:
            continue

        if "axis_center" not in step_info or "calculated_radius" not in step_info or "calculated_z" not in step_info:
            print(f"⚠️ No hay centro/radio/Z en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]
        z_value = step_info["calculated_z"]  # 📌 Usamos el Z_promedio de cada secuencia

        for item in step_info.get("items", []):
            if item.get("Calibration_Status") == "uncalibrated":
                image_number = item.get("ImageNumber", None)
                match = visual_matches[visual_matches[step_name] == image_number]

                if not match.empty:
                    theta = float(match[angle_column].values[0])
                    item["Angular position"] = theta
                    item["Calibration_Status"] = "visually calibrated"

                    # 📌 Convertir Theta en X, Y usando el radio
                    x, y, _ = angle_to_xy(theta, radius)
                    item["X"] = x
                    item["Y"] = y
                    item["Z"] = z_value  # 📌 Ahora cada imagen usa el Z de su secuencia

                    print(f"🔵 {image_number}: Theta asignado = {theta}° → ({x:.3f}, {y:.3f}, {z_value:.3f})")

    print("\n📌 Paso final: Verificación de Theta antes de guardar")

    # 📌 Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Calibración visual completada. JSON guardado en {json_output_path}")
