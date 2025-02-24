import sys
from pathlib import Path
import numpy as np
import math

# Importamos los módulos necesarios de tu repo
from data.json_handler import load_sequences_json, save_sequences_json
from data.pix4d_import import load_pix4d_pose_txt, apply_calibrations_to_json
from data.pix4d_export import export_to_pix4d_csv
from processing.cluster_calibrator import calibrate_all_sequences
from config import CENTER

def compute_sequence_radius(step_info, center):
    """
    Calcula el radio basado en imágenes calibradas dentro de la secuencia.
    Como todas las imágenes en una secuencia tienen el mismo radio,
    tomamos la mediana de la distancia de las calibradas al centro.
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
    return float(np.median(distances)) if distances else None

def update_sequence_radii(all_data, center):
    """
    Para cada StepXX, si no tiene radio definido, lo calculamos con las imágenes calibradas.
    """
    for step_name, step_info in all_data.items():
        radius = compute_sequence_radius(step_info, center)
        if radius is not None:
            step_info["calculated_radius"] = radius
    return all_data

def main():
    if len(sys.argv) < 2:
        print("Uso: python update_positions.py <pix4d_pose.txt> [<output_csv>]")
        sys.exit(1)

    txt_path = Path(sys.argv[1])
    if not txt_path.exists():
        print(f"❌ Error: No se encontró el archivo {txt_path}")
        sys.exit(1)

    output_csv = "output/final_pix4d.csv"
    if len(sys.argv) > 2:
        output_csv = sys.argv[2]

    print("🔹 [1] Cargando JSON principal...")
    all_data = load_sequences_json()

    print(f"🔹 [2] Cargando poses calibradas desde {txt_path} ...")
    calibrations = load_pix4d_pose_txt(txt_path)

    print("🔹 [3] Aplicando calibraciones al JSON...")
    all_data = apply_calibrations_to_json(all_data, calibrations)

    print("🔹 [4] Calculando radios en cada secuencia...")
    all_data = update_sequence_radii(all_data, CENTER)

    print("🔹 [5] Propagando posiciones y orientación en cada cluster...")
    all_data = calibrate_all_sequences(all_data, CENTER)

    print(f"🔹 [6] Exportando CSV final a {output_csv} ...")
    export_to_pix4d_csv(all_data, output_csv)

    print("🔹 [7] Guardando JSON actualizado...")
    save_sequences_json(all_data)

    print("✅ Proceso completo. CSV final disponible en output/.")
    print("✅ JSON actualizado en data/ground_truth/all_sequences.json.")

if __name__ == "__main__":
    main()
