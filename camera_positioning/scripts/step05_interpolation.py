import json
import numpy as np
from processing.angular_transform import angle_to_xy

def interpolate_positions(json_input_path, json_output_path):
    """
    Interpola imágenes 'uncalibrated' y las convierte en 'estimated'.
    1️⃣ Identifica segmentos entre imágenes calibradas ('original' y 'visually calibrated').
    2️⃣ Divide proporcionalmente la diferencia angular ('Theta') en cada segmento.
    3️⃣ Convierte Theta → X, Y, Z usando el radio de la secuencia.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    print("\n📌 Iniciando Step 05: Interpolación de imágenes 'estimated'")

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        if "axis_center" not in step_info or "calculated_radius" not in step_info or "calculated_z" not in step_info:
            print(f"⚠️ No hay centro/radio/Z en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]
        z_value = step_info["calculated_z"]

        # 📌 Identificar segmentos de imágenes no calibradas entre imágenes calibradas
        uncalibrated_segments = []
        current_segment = []
        prev_calibrated = None

        for item in items:
            if item.get("Calibration_Status") in ["original", "visually calibrated"]:
                if prev_calibrated and current_segment:
                    uncalibrated_segments.append((prev_calibrated, item, current_segment))
                    current_segment = []
                prev_calibrated = item
            elif item.get("Calibration_Status") == "uncalibrated":
                current_segment.append(item)

        # 📌 Iterar sobre los segmentos y distribuir Theta proporcionalmente
        for segment in uncalibrated_segments:
            start_calibrated, end_calibrated, segment_items = segment

            # 📌 Verificar que ambos extremos existan
            if not start_calibrated or not end_calibrated:
                print(f"⚠️ Segmento con imágenes calibradas faltantes. Saltando...")
                continue

            start_theta = start_calibrated.get("Angular position")
            end_theta = end_calibrated.get("Angular position")

            if start_theta is None or end_theta is None:
                print(f"⚠️ Segmento entre {start_calibrated.get('ImageNumber', 'Unknown')} y {end_calibrated.get('ImageNumber', 'Unknown')} no puede interpolar Theta.")
                continue

            num_steps = len(segment_items) + 1  # Cantidad de divisiones en el segmento
            theta_step = (end_theta - start_theta) / num_steps  # Paso angular para cada imagen

            for i, item in enumerate(segment_items):
                interpolated_theta = start_theta + (i + 1) * theta_step  # Asignar Theta progresivo

                # 📌 Convertir Theta en X, Y usando el radio
                x, y, _ = angle_to_xy(interpolated_theta, radius)

                # 📌 Actualizar la imagen interpolada
                item["Angular position"] = interpolated_theta
                item["X"] = x
                item["Y"] = y
                item["Z"] = z_value
                item["Calibration_Status"] = "estimated"

                print(f"🔴 {item.get('Filename', 'Unknown')}: Theta interpolado = {interpolated_theta:.3f}° → ({x:.3f}, {y:.3f}, {z_value:.3f})")

    # 📌 Guardar JSON actualizado con Theta distribuido proporcionalmente
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Interpolación completada con segmentos. JSON guardado en {json_output_path}")
