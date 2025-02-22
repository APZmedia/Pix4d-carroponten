import csv
import re
from data.json_handler import set_image_xyz, update_image_status, find_item_by_id

def load_pix4d_calibrations(csv_file):
    """
    Lee un archivo CSV de Pix4D donde cada fila tiene:
    [ImageName, X, Y, Z, Omega, Phi, Kappa, ...]
    Devuelve un dict calibrations[image_id_str] = {info...}.
    Ajusta si tu formato real es distinto.
    """
    calibrations = {}
    with open(csv_file, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)  # lee encabezado si existe
        for row in reader:
            if not row or len(row) < 4:
                continue
            filename = row[0].strip()
            x = float(row[1])
            y = float(row[2])
            z = float(row[3])
            # Suponiendo que Omega,Phi,Kappa están en col[4],col[5],col[6]
            omega = float(row[4]) if len(row) > 4 else 0.0
            phi = float(row[5]) if len(row) > 5 else 0.0
            kappa = float(row[6]) if len(row) > 6 else 0.0

            # Extrae la subcadena con ID (p.ej. '4159') del nombre 'Elettra-Carroponte2024-4159_pt.jpg'
            match = re.search(r"2024-(\d+)_", filename)
            if match:
                image_id_str = match.group(1)  # '4159', por ejemplo
                calibrations[image_id_str] = {
                    "filename": filename,
                    "X": x,
                    "Y": y,
                    "Z": z,
                    "Omega": omega,
                    "Phi": phi,
                    "Kappa": kappa
                }
    return calibrations

def apply_calibrations_to_json(all_data, calibrations):
    """
    Recorre all_data y, para cada imagen con ID en calibrations, actualiza X, Y, Z, 
    y guarda 'Omega', 'Phi', 'Kappa' (si deseas). 
    Marca la imagen como 'original'.
    Las imágenes que no estén en calibrations se marcan 'uncalibrated'.
    """
    # Para luego marcar 'original' o 'uncalibrated'
    calibrated_ids = set(calibrations.keys())

    for image_id_str in calibrated_ids:
        item = find_item_by_id(all_data, image_id_str)
        if item:
            # Actualiza posición
            cal = calibrations[image_id_str]
            set_image_xyz(item, cal["X"], cal["Y"], cal["Z"])
            # Guardar angles:
            item["Omega"] = cal["Omega"]
            item["Phi"] = cal["Phi"]
            item["Kappa"] = cal["Kappa"]
            # Marcamos "original"
            item["Calibration_Status"] = "original"

    # Ahora marcar uncalibrated a los que NO aparecen en calibrations
    update_image_status(all_data, calibrated_ids)

    return all_data
