import json
import numpy as np
from datetime import datetime
from processing.angular_transform import angle_to_xy

def interpolate_positions(json_input_path, json_output_path):
    """
    Interpola imágenes 'uncalibrated' y las convierte en 'estimated'.
    1) Ordena la lista de imágenes por (ImageNumber ASC, Timestamp ASC) para respetar la secuencia lógica.
    2) Identifica segmentos entre imágenes calibradas ('original' o 'visually calibrated').
    3) Divide proporcionalmente la diferencia angular ('Theta') entre dichas imágenes calibradas.
    4) Convierte Theta → X, Y, Z usando el radio y Z definidos en la secuencia.
    5) Finalmente elimina el campo _parsed_ts (datetime) para no romper la serialización.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    print("\n📌 Iniciando Step 05: Interpolación de imágenes 'estimated'")

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        # 1) Verificamos que haya campos clave para poder interpolar
        if "axis_center" not in step_info or "calculated_radius" not in step_info or "calculated_z" not in step_info:
            print(f"⚠️ No hay centro/radio/Z en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]
        z_value = step_info["calculated_z"]

        # 2) Convertir Timestamp a objeto datetime para ordenar
        for item in items:
            try:
                item["_parsed_ts"] = datetime.strptime(item["Timestamp"], "%Y:%m:%d %H:%M:%S")
            except:
                # Si falla la lectura, usamos fecha máxima para que se vaya al final
                item["_parsed_ts"] = datetime.max

        # 3) Reordenar por (ImageNumber, _parsed_ts) ascendente
        # Asegúrate de convertir ImageNumber a int si viene en string
        items.sort(key=lambda x: (int(x["ImageNumber"]), x["_parsed_ts"]))

        # 4) Identificar segmentos de uncalibrated entre calibradas
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

        # 5) Interpolar dentro de cada segmento
        for segment in uncalibrated_segments:
            start_calibrated, end_calibrated, segment_items = segment

            start_theta = start_calibrated.get("Angular position")
            end_theta = end_calibrated.get("Angular position")

            if start_theta is None or end_theta is None:
                print(
                    f"⚠️ Segmento entre {start_calibrated.get('ImageNumber', 'Unknown')} "
                    f"y {end_calibrated.get('ImageNumber', 'Unknown')} "
                    "no puede interpolar Theta (falta 'Angular position')."
                )
                continue

            num_steps = len(segment_items) + 1
            theta_step = (end_theta - start_theta) / num_steps

            for i, item in enumerate(segment_items):
                interpolated_theta = start_theta + (i + 1) * theta_step
                x, y, _ = angle_to_xy(interpolated_theta, radius)

                item["Angular position"] = interpolated_theta
                item["X"] = x
                item["Y"] = y
                item["Z"] = z_value
                item["Calibration_Status"] = "estimated"

                print(
                    f"🔴 {item.get('Filename', 'Unknown')}: "
                    f"Theta interpolado = {interpolated_theta:.3f}° → ({x:.3f}, {y:.3f}, {z_value:.3f})"
                )

    # 6) Eliminar el campo '_parsed_ts' (objeto datetime) para poder serializar a JSON sin errores
    for step_name, step_info in sequences_data.items():
        for item in step_info.get("items", []):
            if "_parsed_ts" in item:
                del item["_parsed_ts"]

    # 7) Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Interpolación completada. JSON guardado en {json_output_path}")
