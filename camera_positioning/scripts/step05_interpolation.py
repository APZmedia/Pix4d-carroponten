import json
import numpy as np
from datetime import datetime
from scipy.signal import savgol_filter
from processing.angular_transform import angle_to_xy

def interpolate_positions(json_input_path, json_output_path):
    """
    Interpola imágenes 'uncalibrated' y las convierte en 'estimated'.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    print("\n📌 Iniciando Step 05: Interpolación de imágenes 'estimated'")

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        # Validar que existan datos clave para la interpolación
        if "axis_center" not in step_info or "calculated_radius" not in step_info or "calculated_z" not in step_info:
            print(f"⚠️ No hay centro/radio/Z en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]
        z_value = step_info["calculated_z"]

        # Convertir Timestamp a datetime para ordenar
        for item in items:
            try:
                item["_parsed_ts"] = datetime.strptime(item["Timestamp"], "%Y-%m-%d %H:%M:%S") if item["Timestamp"] else None
            except:
                item["_parsed_ts"] = None

        # Ordenar asegurando que los valores None no rompan la secuencia
        items.sort(key=lambda x: (int(x["ImageNumber"]), x["_parsed_ts"] if x["_parsed_ts"] else datetime.max))

        # Identificar segmentos de uncalibrated entre calibradas
        uncalibrated_segments = []
        current_segment = []
        prev_calibrated = None

        for item in items:
            status = item.get("Calibration_Status")
            if status in ["original", "visually calibrated"]:
                if prev_calibrated and current_segment:
                    uncalibrated_segments.append((prev_calibrated, item, current_segment))
                    current_segment = []
                prev_calibrated = item
            elif status == "uncalibrated":
                current_segment.append(item)

        # Interpolar dentro de cada segmento
        for segment in uncalibrated_segments:
            start_calibrated, end_calibrated, segment_items = segment
            start_theta = start_calibrated.get("Angular position")
            end_theta = end_calibrated.get("Angular position")

            if start_theta is None or end_theta is None or abs(start_theta - end_theta) < 0.01:
                print(f"⚠️ Segmento entre {start_calibrated.get('ImageNumber', 'Unknown')} y {end_calibrated.get('ImageNumber', 'Unknown')} no puede interpolar Theta.")
                continue

            num_steps = len(segment_items) + 1
            if abs(start_theta - end_theta) < 1:
                theta_values = np.full(len(segment_items), start_theta)  # Propagar último valor válido
            else:
                theta_values = np.linspace(start_theta, end_theta, num_steps + 1)[1:-1]

            # Aplicar suavizado para evitar saltos abruptos
            if len(theta_values) >= 3:
                theta_values = savgol_filter(theta_values, min(len(theta_values), 3), 2)

            for i, item in enumerate(segment_items):
                interpolated_theta = theta_values[i]
                x, y, _ = angle_to_xy(interpolated_theta, radius)

                item["Angular position"] = interpolated_theta
                item["X"] = x
                item["Y"] = y
                item["Z"] = z_value
                item["Calibration_Status"] = "estimated"

        # Eliminar '_parsed_ts' para serialización
        for item in items:
            if "_parsed_ts" in item:
                del item["_parsed_ts"]

    # Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Interpolación completada con correcciones. JSON guardado en {json_output_path}")
