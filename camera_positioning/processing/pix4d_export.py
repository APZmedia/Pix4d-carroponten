import csv
import math

def export_to_pix4d_csv(all_data, output_csv):
    """
    Genera un CSV con las columnas:
    Filename, X, Y, Z, Omega, Phi, Kappa, SigmaHoriz, SigmaVert
    con margen de error distinto si la imagen es 'original' o 'estimated'.
    """
    with open(output_csv, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert"])

        for step_name, step_info in all_data.items():
            for item in step_info["items"]:
                filename = item["Filename"]
                X = float(item.get("X", 0.0))
                Y = float(item.get("Y", 0.0))
                Z = float(item.get("Z", 0.0))

                # Si tienes guardados 'Omega','Phi','Kappa', úsalos. Si no, pon 0.0.
                Omega = float(item.get("Omega", 0.0))
                Phi = float(item.get("Phi", 0.0))
                Kappa = float(item.get("Kappa", 0.0))

                # Define márgenes
                status = item.get("Calibration_Status", "uncalibrated")
                if status == "original":
                    sigma_h, sigma_v = 0.5, 0.2  # Ejemplo
                elif status == "estimated":
                    sigma_h, sigma_v = 2.0, 0.2
                else:
                    sigma_h, sigma_v = 5.0, 1.0  # Si queda uncalibrated

                writer.writerow([filename, X, Y, Z, Omega, Phi, Kappa, sigma_h, sigma_v])
