import csv
import json

def export_to_pix4d_csv(all_data, output_csv):
    """
    Genera un CSV con las columnas:
    Filename, X, Y, Z, Omega, Phi, Kappa, SigmaHoriz, SigmaVert
    ajustando los márgenes de error para Pix4D, y exportando
    únicamente imágenes con Calibration_Status == 'visually calibrated' o 'estimated'.
    """
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert"])

        for step_name, step_info in all_data.items():
            for item in step_info["items"]:
                status = item.get("Calibration_Status", "uncalibrated")

                # Filtrar: solo 'visually calibrated' o 'estimated'
                if status not in ("visually calibrated", "estimated"):
                    continue

                filename = item.get("Filename", "Unnamed")
                X = float(item.get("X", 0.0))
                Y = float(item.get("Y", 0.0))
                Z = float(item.get("Z", 0.0))

                Omega = float(item.get("Omega", 0.0))
                Phi = float(item.get("Phi", 0.0))
                Kappa = float(item.get("Kappa", 0.0))

                # Definir márgenes según estado
                if status == "visually calibrated":
                    sigma_h, sigma_v = 1.0, 0.3
                else:  # status == "estimated"
                    sigma_h, sigma_v = 2.0, 0.5

                writer.writerow([filename, X, Y, Z, Omega, Phi, Kappa, sigma_h, sigma_v])

def run_step08(json_input_path, csv_output_path):
    """
    Ejecuta Step 08: Exportar los datos a CSV en formato Pix4D
    (solo 'visually calibrated' y 'estimated').
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    export_to_pix4d_csv(sequences_data, csv_output_path)

    print(f"✅ Exportación a CSV completada. Archivo guardado en {csv_output_path}")
    return f"✅ Exportación a CSV completada. Archivo guardado en {csv_output_path}"


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python step08_export_csv.py <json_entrada> <csv_salida>")
        sys.exit(1)

    json_input_path = sys.argv[1]
    csv_output_path = sys.argv[2]

    run_step08(json_input_path, csv_output_path)
