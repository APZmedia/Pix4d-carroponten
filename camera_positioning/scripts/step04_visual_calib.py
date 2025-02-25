import json
import numpy as np
import pandas as pd

def angular_to_cartesian(angle, center_x, center_y, radius):
    """
    Convierte un ángulo en coordenadas cartesianas usando centro y radio.
    """
    angle_rad = np.radians(angle)
    x = center_x + radius * np.cos(angle_rad)
    y = center_y + radius * np.sin(angle_rad)
    return x, y

def calibrate_visually(json_input_path, csv_input_path, json_output_path):
    """
    Calibra imágenes no calibradas usando información del CSV con posiciones angulares.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    # 📌 Cargar el CSV con las correspondencias visuales
    visual_matches = pd.read_csv(csv_input_path)
    
    # Verificar que las columnas necesarias están en el CSV
    if not {"ImageName", "AngularPosition"}.issubset(visual_matches.columns):
        raise ValueError("El CSV debe contener las columnas 'ImageName' y 'AngularPosition'.")

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        # 📌 Obtener el centro y radio de la secuencia
        if "axis_center" not in step_info or "calculated_radius" not in step_info:
            print(f"⚠️ No hay centro/radio en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]

        for item in items:
            if item.get("Calibration_Status") == "uncalibrated":
                filename = item.get("Filename", "").strip()

                # 📌 Buscar la imagen en el CSV
                match = visual_matches[visual_matches["ImageName"] == filename]
                
                if not match.empty:
                    angle = float(match["AngularPosition"].values[0])

                    # 📌 Convertir a coordenadas cartesianas
                    x, y = angular_to_cartesian(angle, center_x, center_y, radius)

                    # 📌 Actualizar el JSON
                    item["X"] = x
                    item["Y"] = y
                    item["Calibration_Status"] = "visually calibrated"

                    print(f"✅ {filename}: {angle}° → ({x:.3f}, {y:.3f})")

    # 📌 Guardar el JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Calibración visual completada. JSON guardado en {json_output_path}")
