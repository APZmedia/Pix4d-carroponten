import json
import numpy as np
from processing.angular_transform import angle_to_xy

def interpolate_orientation(theta, angles, values):
    """Interpola Omega, Phi y Kappa asegurando continuidad en 360°."""
    return np.interp(theta, angles, values, period=360)  # Maneja la rotación correctamente

def propagate_orientation(json_input_path, json_output_path):
    """
    Propaga la orientación (Omega, Phi, Kappa) en imágenes 'visually calibrated' y 'estimated'
    usando el patrón de rotación identificado en imágenes 'original'.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        # Extraer datos de rotación de imágenes 'original'
        original_items = [item for item in items if item.get("Calibration_Status") == "original"]
        
        if len(original_items) > 1:
            angles = np.array([item.get("Angular position") for item in original_items])
            omegas = np.array([item.get("Omega") for item in original_items])
            phis = np.array([item.get("Phi") for item in original_items])
            kappas = np.array([item.get("Kappa") for item in original_items])

            for item in items:
                if item.get("Calibration_Status") in ["visually calibrated", "estimated"]:
                    theta = item.get("Angular position")
                    if theta is not None:
                        item["Omega"] = interpolate_orientation(theta, angles, omegas)
                        item["Phi"] = interpolate_orientation(theta, angles, phis)
                        item["Kappa"] = interpolate_orientation(theta, angles, kappas)
                        
                        print(f"🔄 {item.get('Filename', 'Unknown')}: "
                              f"Interpolated Omega: {item['Omega']:.3f}, Phi: {item['Phi']:.3f}, Kappa: {item['Kappa']:.3f}")

    # Guardar JSON actualizado con la orientación propagada
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Propagación de orientación completada. JSON guardado en {json_output_path}")

