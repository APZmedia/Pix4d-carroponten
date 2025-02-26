import json
import pandas as pd
import numpy as np
from processing.angular_transform import angle_to_xy

def interpolate_theta(prev_theta, next_theta, factor):
    """
    Interpola Theta de forma equidistante entre dos valores.
    """
    return prev_theta + factor * (next_theta - prev_theta)

def interpolate_positions(json_input_path, json_output_path):
    """
    Interpola imágenes 'uncalibrated' y las convierte en 'estimated'.
    1️⃣ Encuentra intervalos entre imágenes 'original' y 'visually calibrated'.
    2️⃣ Interpola Theta de forma equidistante.
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

        # Encontrar imágenes calibradas
        calibrated_indices = [i for i, item in enumerate(items) if item.get("Calibration_Status") in ["original", "visually calibrated"]]
        estimated_indices = [i for i, item in enumerate(items) if item.get("Calibration_Status") == "uncalibrated"]

        for idx in estimated_indices:
            prev_idx = max([i for i in calibrated_indices if i < idx], default=None)
            next_idx = min([i for i in calibrated_indices if i > idx], default=None)

            if prev_idx is not None and next_idx is not None:
                prev_theta = items[prev_idx].get("Angular position")
                next_theta = items[next_idx].get("Angular position")

                if prev_theta is not None and next_theta is not None:
                    # Calcular factor de interpolación basado en la posición en la secuencia
                    factor = (idx - prev_idx) / (next_idx - prev_idx)
                    interpolated_theta = interpolate_theta(prev_theta, next_theta, factor)

            elif prev_idx is not None:  # Solo hay una imagen calibrada antes
                interpolated_theta = items[prev_idx].get("Angular position")

            elif next_idx is not None:  # Solo hay una imagen calibrada después
                interpolated_theta = items[next_idx].get("Angular position")
            
            else:
                print(f"⚠️ {items[idx].get('Filename', 'Unknown')}: No tiene imágenes calibradas cercanas para interpolar Theta.")
                continue  # No se puede interpolar, pasar a la siguiente imagen

            # Asignar el Theta interpolado antes de calcular (X, Y)
            items[idx]["Angular position"] = interpolated_theta

            # Convertir Theta en X, Y usando el radio
            x, y, _ = angle_to_xy(interpolated_theta, radius)

            # Actualizar la imagen interpolada
            items[idx]["X"] = x
            items[idx]["Y"] = y
            items[idx]["Z"] = z_value
            items[idx]["Calibration_Status"] = "estimated"

            print(f"🔴 {items[idx].get('Filename', 'Unknown')}: Theta interpolado = {interpolated_theta}° → ({x:.3f}, {y:.3f}, {z_value:.3f})")

    # Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Interpolación completada. JSON guardado en {json_output_path}")
