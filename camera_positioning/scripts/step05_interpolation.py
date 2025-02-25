import json
import numpy as np
from processing.angular_transform import angle_to_xy

def interpolate_positions(json_input_path, json_output_path):
    """
    Interpola la posición de imágenes sin calibrar siguiendo un movimiento circular equidistante.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        if "axis_center" not in step_info or "calculated_radius" not in step_info:
            print(f"⚠️ No hay centro/radio en {step_name}. Saltando...")
            continue

        center_x = step_info["axis_center"]["x"]
        center_y = step_info["axis_center"]["y"]
        radius = step_info["calculated_radius"]

        # 📌 Obtener índices de imágenes calibradas y sin calibrar
        calibrated_indices = [i for i, item in enumerate(items) if item.get("Calibration_Status") in ["calibrated", "visually calibrated"]]
        uncalibrated_indices = [i for i, item in enumerate(items) if item.get("Calibration_Status") == "uncalibrated"]

        if not calibrated_indices or not uncalibrated_indices:
            print(f"⚠️ No hay suficientes imágenes calibradas para interpolar en {step_name}.")
            continue

        i = 0
        while i < len(uncalibrated_indices):
            idx = uncalibrated_indices[i]

            # 📌 Buscar imágenes calibradas antes y después
            prev_idx = max([i for i in calibrated_indices if i < idx], default=None)
            next_idx = min([i for i in calibrated_indices if i > idx], default=None)

            if prev_idx is None or next_idx is None:
                i += 1
                continue

            # 📌 Obtener ángulos de las imágenes antes y después
            prev_item = items[prev_idx]
            next_item = items[next_idx]

            theta_prev = np.degrees(np.arctan2(prev_item["Y"] - center_y, prev_item["X"] - center_x))
            theta_next = np.degrees(np.arctan2(next_item["Y"] - center_y, next_item["X"] - center_x))

            # 📌 Corregir valores negativos de ángulo
            theta_prev = (theta_prev + 360) % 360
            theta_next = (theta_next + 360) % 360

            # 📌 Obtener los índices de imágenes sin calibrar en este intervalo
            interval_indices = [j for j in uncalibrated_indices if prev_idx < j < next_idx]

            if len(interval_indices) > 0:
                # 📌 Calcular los ángulos equidistantes
                angles = np.linspace(theta_prev, theta_next, len(interval_indices) + 2)[1:-1]

                for j, theta_interp in zip(interval_indices, angles):
                    x_interp, y_interp, _ = angle_to_xy(theta_interp, radius)

                    # 📌 Usar el mismo `Z` de la imagen calibrada anterior
                    items[j]["X"] = x_interp
                    items[j]["Y"] = y_interp
                    items[j]["Z"] = prev_item["Z"]
                    items[j]["Calibration_Status"] = "estimated"

                    print(f"✅ Interpolado {items[j]['Filename']}: ({x_interp:.3f}, {y_interp:.3f}, {prev_item['Z']:.3f}) con ángulo {theta_interp:.2f}°")

            i += len(interval_indices)  # Saltamos al siguiente intervalo

    # 📌 Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Interpolación completada. JSON guardado en {json_output_path}")
