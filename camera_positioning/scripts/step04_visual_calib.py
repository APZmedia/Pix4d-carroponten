import json
import pandas as pd
from processing.angular_transform import angle_to_xy

def calibrate_visually(json_input_path, csv_input_path, json_output_path):
    """
    Calibra imágenes no calibradas usando información del CSV con posiciones angulares.
    Solo afecta imágenes con Calibration_Status = "uncalibrated".
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    visual_matches = pd.read_csv(csv_input_path)

    sequence_columns = list(visual_matches.columns[1:-1])  # Todas las secuencias menos "LandmarkID" y "Theta"
    angle_column = "Theta"

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        if step_name not in sequence_columns:
            print(f"⚠️ No hay datos en el CSV para {step_name}. Saltando...")
            continue

        if "axis_center" not in step_info or "calculated_radius" not in step_info or "calculated_z" not in step_info:
            print(f"⚠️ No hay centro/radio/Z en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]
        z_value = step_info["calculated_z"]  # 📌 Usamos el Z_promedio de cada secuencia

        for item in items:
            if item.get("Calibration_Status") == "uncalibrated":
                image_number = item.get("ImageNumber", None)
                match = visual_matches[visual_matches[step_name] == image_number]

                if not match.empty:
                    angle = float(match[angle_column].values[0])
                    x, y, _ = angle_to_xy(angle, radius)

                    item["X"] = x
                    item["Y"] = y
                    item["Z"] = z_value  # 📌 Ahora cada imagen usa el Z de su secuencia
                    item["Calibration_Status"] = "visually calibrated"

                    print(f"✅ {image_number}: {angle}° → ({x:.3f}, {y:.3f}, {z_value:.3f})")

    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Calibración visual completada. JSON guardado en {json_output_path}")
