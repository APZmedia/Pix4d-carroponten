import re
import json

def parse_pix4d_calibrated_txt(file_path):
    """
    Parsea un archivo de parámetros externos de cámara calibrados de Pix4D.
    Extrae los valores de X, Y, Z y los ángulos Omega, Phi, Kappa.
    """
    calibrated_data = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Expresión regular para capturar las líneas con los parámetros
    pattern = re.compile(r"(?P<filename>\S+)\s+(?P<x>-?\d+\.\d+)\s+(?P<y>-?\d+\.\d+)\s+(?P<z>-?\d+\.\d+)\s+(?P<omega>-?\d+\.\d+)\s+(?P<phi>-?\d+\.\d+)\s+(?P<kappa>-?\d+\.\d+)")
    
    for line in lines:
        match = pattern.match(line)
        if match:
            filename = match.group("filename")
            calibrated_data[filename] = {
                "X": float(match.group("x")),
                "Y": float(match.group("y")),
                "Z": float(match.group("z")),
                "Omega": float(match.group("omega")),
                "Phi": float(match.group("phi")),
                "Kappa": float(match.group("kappa")),
                "Calibration_Status": "calibrated"
            }
    
    return calibrated_data


def save_calibrated_json(calibrated_data, output_path):
    """
    Guarda los datos calibrados en un archivo JSON.
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(calibrated_data, f, indent=4)
    print(f"Datos calibrados guardados en {output_path}")


# Uso del script
if __name__ == "__main__":
    input_file = "XPR-finalmerge03_rebuild_calibrated_external_camera_parameters.txt"
    output_json = "calibrated_camera_data.json"
    
    calibrated_data = parse_pix4d_calibrated_txt(input_file)
    save_calibrated_json(calibrated_data, output_json)
    
    print(f"Se encontraron {len(calibrated_data)} imágenes calibradas.")
