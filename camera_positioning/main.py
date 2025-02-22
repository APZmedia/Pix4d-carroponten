import sys
import os
from pathlib import Path

# Importa los módulos del pipeline
from data.json_handler import load_sequences_json, save_sequences_json
from processing.cluster_calibrator import calibrate_all_sequences
from config import CENTER
from ui.ui_app import launch_ui  # Importamos la UI

import json
import csv
import io

#########################
# Funciones del pipeline CLI
#########################

def parse_initial_txt(txt_path):
    """
    Procesa el archivo TXT inicial. Modifícalo según la lógica que necesites.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return {
        "num_lines": len(lines),
        "lines": lines
    }

def compute_sequence_radius(step_info, center):
    """
    Calcula el radio usando imágenes calibradas.
    """
    import numpy as np
    distances = [
        np.linalg.norm([item["X"] - center[0], item["Y"] - center[1]])
        for item in step_info["items"]
        if item.get("Calibration_Status") == "original" and item.get("X") is not None
    ]
    return float(np.median(distances)) if distances else None

def update_sequence_radii(all_data, center):
    """
    Para cada secuencia, si no tiene radio, lo calcula.
    """
    for step_name, step_info in all_data.items():
        radius = compute_sequence_radius(step_info, center)
        if radius is not None:
            step_info["calculated_radius"] = radius
    return all_data

def run_pipeline_cli(txt_path=None):
    """
    Ejecuta el pipeline en modo CLI sin UI.
    """
    print("[1] Cargando JSON desde data/ground_truth/all_sequences.json...")
    all_data = load_sequences_json()

    if txt_path:
        print(f"[2] Procesando archivo TXT: {txt_path}...")
        txt_info = parse_initial_txt(txt_path)
        print(f"TXT contiene {txt_info['num_lines']} líneas.")

    print("[3] Calculando radios de cada secuencia...")
    all_data = update_sequence_radii(all_data, CENTER)

    print("[4] Ejecutando calibración de clusters...")
    all_data = calibrate_all_sequences(all_data, CENTER)

    print("[5] Guardando JSON actualizado...")
    save_sequences_json(all_data)

    output_csv_path = "output/final_pix4d.csv"
    print(f"[6] Generando CSV en {output_csv_path}...")
    generate_pix4d_csv(all_data, output_csv_path)

    print("✅ Proceso completado. Revisa la carpeta output/ para el CSV final.")

def generate_pix4d_csv(all_data, output_csv_path):
    """
    Genera un CSV con formato Pix4D.
    """
    with open(output_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert"])

        for step_name, step_info in all_data.items():
            for item in step_info["items"]:
                fname = item["Filename"]
                x = float(item.get("X", 0.0))
                y = float(item.get("Y", 0.0))
                z = float(item.get("Z", 0.0))
                Omega = float(item.get("Omega", 0.0))
                Phi = float(item.get("Phi", 0.0))
                Kappa = float(item.get("Kappa", 0.0))

                status = item.get("Calibration_Status", "uncalibrated")
                sigma_h, sigma_v = (0.5, 0.2) if status == "original" else (2.0, 0.2) if status == "estimated" else (5.0, 1.0)

                writer.writerow([fname, x, y, z, Omega, Phi, Kappa, sigma_h, sigma_v])

#########################
# Lógica de ejecución
#########################

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Si se pasa un argumento (TXT), ejecutamos en modo CLI
        txt_file = sys.argv[1]
        if not Path(txt_file).exists():
            print(f"❌ Error: No se encontró el archivo {txt_file}")
            sys.exit(1)
        run_pipeline_cli(txt_file)
    else:
        # Si no hay argumentos, lanzamos la UI
        print("🖥 Iniciando UI interactiva con Gradio...")
        demo_app = launch_ui()
        demo_app.launch()
