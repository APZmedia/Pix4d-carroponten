import sys
import os
import numpy as np
from pathlib import Path

# Importa tus módulos
from data.json_handler import load_sequences_json, save_sequences_json
from data.json_handler import get_image_id_from_item, set_image_xyz
from data.pix4d_import import load_pix4d_calibrations, apply_calibrations_to_json
from data.pix4d_export import export_to_pix4d_csv
from processing.cluster_calibrator import calibrate_all_sequences
from config import CENTER
import math

def compute_sequence_radius(step_info, center):
    """
    Calcula el radio mediano usando las imágenes 'original' (calibradas).
    """
    distances = []
    for item in step_info["items"]:
        if item.get("Calibration_Status") == "original":
            x, y = item.get("X"), item.get("Y")
            if x is not None and y is not None:
                dx = x - center[0]
                dy = y - center[1]
                dist = math.sqrt(dx*dx + dy*dy)
                distances.append(dist)
    if len(distances) == 0:
        return None
    return float(np.median(distances))

def update_sequence_radii(all_data, center):
    """
    Para cada StepXX, si 'calculated_radius' no existe o es 0, lo calculamos.
    """
    for step_name, step_info in all_data.items():
        radius = compute_sequence_radius(step_info, center)
        if radius is not None:
            step_info["calculated_radius"] = radius
    return all_data

def main():
    if len(sys.argv) < 3:
        print("Uso: python update_positions.py <pix4d_calib.csv> <output_csv>")
        print("Ejemplo: python update_positions.py input/calibradas.csv output/final_pix4d.csv")
        sys.exit(1)
    
    pix4d_csv_path = Path(sys.argv[1])
    output_csv_path = Path(sys.argv[2])

    # 1) Cargar JSON
    print("[1] Cargando JSON...")
    all_data = load_sequences_json()

    # 2) Cargar calibraciones Pix4D
    print("[2] Cargando calibraciones de Pix4D...")
    calibrations = load_pix4d_calibrations(pix4d_csv_path)

    # 3) Aplicar calibraciones a JSON
    print("[3] Aplicando calibraciones...")
    all_data = apply_calibrations_to_json(all_data, calibrations)

    # 4) Calcular radio secuencial (si no está definido)
    print("[4] Calculando/actualizando radios de cada Step...")
    all_data = update_sequence_radii(all_data, CENTER)

    # 5) Propagar posiciones y orientaciones con cluster_calibrator
    print("[5] Propagando estimaciones en cada Step/Cluster...")
    from processing.cluster_calibrator import calibrate_all_sequences
    all_data = calibrate_all_sequences(all_data, CENTER)

    # 6) Exportar CSV final para Pix4D
    print(f"[6] Exportando CSV final => {output_csv_path}...")
    export_to_pix4d_csv(all_data, output_csv_path)

    # 7) Guardar JSON final
    print("[7] Guardando JSON final con datos actualizados...")
    save_sequences_json(all_data)

    print("Proceso completado.")

if __name__ == "__main__":
    main()
