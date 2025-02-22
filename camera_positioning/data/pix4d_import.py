import csv
import re
from data.json_handler import set_image_xyz, update_image_status, find_item_by_id

def load_pix4d_pose_txt(txt_path):
    """
    Lee un archivo de Pix4D con encabezado estilo:
    imageName, cameraIndex, cameraName, X_opt, Y_opt, Z_opt, X_gps, Y_gps, ...
    y columnas para X_opt, Y_opt, Z_opt, Omega, Phi, Kappa, etc.

    Retorna un dict calibrations[image_id_str] = {
        "filename": str,
        "X": float,
        "Y": float,
        "Z": float,
        "Omega": float,
        "Phi": float,
        "Kappa": float,
        # ... si necesitas otras col se pueden agregar
    }

    Se basa en los nombres de columna para encontrar su índice (robusto),
    y extrae el ID de la imagen a partir de '2024-(\d+)_' en el nombre.
    """
    calibrations = {}
    with open(txt_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        headers = next(reader, None)  # Lee la fila de encabezados

        if not headers:
            return calibrations  # archivo vacío o sin encabezado

        # Mapeamos los nombres de columnas que nos interesan
        col_map = {}
        # Lista de columnas clave que podrías necesitar
        columns_needed = [
            "imageName",  # para extraer el nombre e ID
            "X_opt",
            "Y_opt",
            "Z_opt",
            "Omega",
            "Phi",
            "Kappa",
        ]
        # Si en tu TXT hay otras columnas (X_gps, X_uncertainty, etc.) y las quieres,
        # añádelas en columns_needed y proceso similar.

        # Localiza índices por nombre
        for cname in columns_needed:
            if cname in headers:
                col_map[cname] = headers.index(cname)

        # Recorremos las filas
        for row in reader:
            if not row or len(row) < len(col_map):
                continue

            # Obtenemos el nombre de la imagen
            if "imageName" not in col_map:
                continue
            image_name = row[col_map["imageName"]].strip()

            # Extraemos ID (p.ej. '4014' de "Elettra-Carroponte2024-4014_pt.jpg")
            match = re.search(r"2024-(\d+)_", image_name)
            if not match:
                # Si no coincide el patrón, lo ignoramos
                continue
            image_id_str = match.group(1)  # p.ej. '4014'

            # Intentamos parsear X_opt, Y_opt, Z_opt, Omega, Phi, Kappa
            def get_float(col):
                if col in col_map:
                    val_str = row[col_map[col]].strip()
                    try:
                        return float(val_str)
                    except ValueError:
                        return 0.0
                return 0.0

            X = get_float("X_opt")
            Y = get_float("Y_opt")
            Z = get_float("Z_opt")
            Omega = get_float("Omega")
            Phi   = get_float("Phi")
            Kappa = get_float("Kappa")

            calibrations[image_id_str] = {
                "filename": image_name,
                "X": X,
                "Y": Y,
                "Z": Z,
                "Omega": Omega,
                "Phi": Phi,
                "Kappa": Kappa,
            }

    return calibrations

def apply_calibrations_to_json(all_data, calibrations):
    """
    Recorre el 'all_data' (que es el JSON con StepXX -> items) y, para cada ID,
    actualiza la posición (X,Y,Z) y los ángulos (Omega,Phi,Kappa).
    Marca la imagen como 'original' (calibrada) si aparece en calibrations.

    El resto de imágenes se marcan como 'uncalibrated'.
    """
    # IDs calibrados
    calibrated_ids = set(calibrations.keys())

    # Asignamos X, Y, Z, Omega, etc. a las imágenes que coincidan
    for image_id_str in calibrated_ids:
        item = find_item_by_id(all_data, image_id_str)
        if item:
            cinfo = calibrations[image_id_str]
            # Actualizamos X, Y, Z:
            set_image_xyz(item, cinfo["X"], cinfo["Y"], cinfo["Z"])
            # Guardamos Omega, Phi, Kappa:
            item["Omega"] = cinfo["Omega"]
            item["Phi"]   = cinfo["Phi"]
            item["Kappa"] = cinfo["Kappa"]
            # Marcamos calibrada
            item["Calibration_Status"] = "original"

    # El resto se marca "uncalibrated"
    update_image_status(all_data, calibrated_ids)

    return all_data
