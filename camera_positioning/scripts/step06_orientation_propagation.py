import json
import numpy as np
from processing.angular_transform import angle_to_xy
from processing.orientation_corrector import infer_orientation_from_polar

def interpolate_orientation(theta, angles, values):
    """Interpola Omega, Phi y Kappa asegurando continuidad en 360°."""
    return np.interp(theta, angles, values, period=360)  # Maneja la rotación circular

def propagate_orientation(json_input_path, json_output_path):
    """
    Propaga la orientación (Omega, Phi, Kappa) en imágenes 'visually calibrated' y 'estimated'
    usando el patrón de rotación identificado en imágenes 'original', ajustando Kappa con modelo polar.
    
    Se asume que cada Step (step_info) tiene 'axis_center': {"x": ..., "y": ...} para usar como 'center'.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])
        
        # Leer el 'center' de este Step desde axis_center. Asegúrate de que exista en el JSON.
        axis_center = step_info.get("axis_center")
        if not axis_center:
            print(f"⚠️ En {step_name} no se encontró 'axis_center'; saltando propagación de orientación.")
            continue
        
        # Conviértelo a la lista que necesites. Ej. [x, y] o [x, y, z] si aplica.
        center = [axis_center["x"], axis_center["y"]]
        
        # Extraer datos de rotación (Omega, Phi, Kappa) de imágenes 'original'
        original_items = [it for it in items if it.get("Calibration_Status") == "original"]
        
        # Para interpolar, necesitamos al menos 2 imágenes 'original'
        if len(original_items) > 1:
            # Extraer arrays con Theta, Omega, Phi y Kappa de esas imágenes
            angles = np.array([it.get("Theta", 0.0) for it in original_items])
            omegas = np.array([it.get("Omega", 0.0) for it in original_items])
            phis   = np.array([it.get("Phi",  0.0) for it in original_items])
            kappas = np.array([it.get("Kappa",0.0) for it in original_items])

            for it in items:
                status = it.get("Calibration_Status")
                # Solo procesamos las que están 'visually calibrated' o 'estimated'
                if status in ["visually calibrated", "estimated"]:
                    theta = it.get("Theta")
                    if theta is not None:
                        # 1) Interpolar Omega y Phi en función de Theta
                        it["Omega"] = interpolate_orientation(theta, angles, omegas)
                        it["Phi"]   = interpolate_orientation(theta, angles, phis)

                        # 2) Ajustar Kappa usando la lógica polar
                        it["Kappa"] = infer_orientation_from_polar(it, center, original_items)

                        print(f"🔄 {it.get('Filename', 'Unknown')} → "
                              f"Omega: {it['Omega']:.3f}, Phi: {it['Phi']:.3f}, "
                              f"Kappa ajustado: {it['Kappa']:.3f}")
        else:
            print(f"ℹ️ En {step_name} no hay suficientes 'original' para interpolar orientación (min 2).")

    # Guardar JSON actualizado con la orientación propagada
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"✅ Propagación de orientación completada. JSON guardado en {json_output_path}")
