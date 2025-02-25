import json
import os

def parse_calibration_txt(txt_file_path):
    """
    Lee un archivo .txt que contiene datos de calibración para cada imagen.
    Se espera que cada línea tenga la siguiente estructura (o similar):
    
        ImageNumber  X   Y   Z   Omega   Phi   Kappa
    
    Se puede ajustar según el formato real de tu .txt.
    
    Retorna:
        dict con clave = ImageNumber (str) y valor = {
            "X": float,
            "Y": float,
            "Z": float,
            "Omega": float (opt),
            "Phi": float (opt),
            "Kappa": float (opt)
        }
    """
    calibration_data = {}
    
    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    # Asumiendo que la primera línea puede ser cabecera; si no, se ajusta
    # Por ejemplo: "ImageNumber  X  Y  Z  Omega  Phi  Kappa"
    header = True
    for line in lines:
        # Si hay cabecera, la saltamos y seteamos header=False
        if header:
            header = False
            continue
        
        parts = line.strip().split()
        # Se ajusta según la estructura que tengas en tu txt
        # Ejemplo: 4335  3.4512  -1.1098  5.62   -0.01   0.02   180.5
        if len(parts) < 4:
            continue  # al menos debe haber ID y 3 coords
        
        image_id = parts[0].strip()
        
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        
        # Omega, Phi, Kappa pueden o no existir
        # Usamos un get index dentro de 'parts' si está disponible
        omega = float(parts[4]) if len(parts) > 4 else 0.0
        phi   = float(parts[5]) if len(parts) > 5 else 0.0
        kappa = float(parts[6]) if len(parts) > 6 else 0.0
        
        calibration_data[image_id] = {
            "X": x,
            "Y": y,
            "Z": z,
            "Omega": omega,
            "Phi": phi,
            "Kappa": kappa,
        }
    
    return calibration_data


def update_json_with_calibration(
    json_input_path, 
    json_output_path, 
    calibration_data,
    image_identifier_key="ImageNumber"
):
    """
    Carga un JSON de secuencias (StepXX), actualiza las imágenes con la info
    presente en `calibration_data` (dict con coords y orientación),
    y guarda un nuevo archivo JSON.

    - `image_identifier_key` indica qué campo en el JSON corresponde a la
      llave para cruzar datos (por ejemplo, "ImageNumber" o "Filename").
    - Si la imagen está en `calibration_data`, se actualizan X, Y, Z y orientaciones
      y se setea `Calibration_Status = "calibrated"`.
    - Si no está, se setea `Calibration_Status = "uncalibrated"`.
    """
    # 1. Cargar el JSON
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)
    
    # 2. Recorrer cada secuencia
    for step_name, step_info in sequences_data.items():
        # Verificar que haya items
        items = step_info.get("items", [])
        
        for item in items:
            # Identificamos la imagen
            image_id = str(item.get(image_identifier_key, "")).strip()
            
            if image_id in calibration_data:
                # => Imagen aparece en .txt => Actualizamos coords y orientación
                cal_info = calibration_data[image_id]
                item["X"] = cal_info["X"]
                item["Y"] = cal_info["Y"]
                item["Z"] = cal_info["Z"]
                
                # Guardamos Omega/Phi/Kappa si quieres:
                item["Omega"] = cal_info.get("Omega", 0.0)
                item["Phi"]   = cal_info.get("Phi", 0.0)
                item["Kappa"] = cal_info.get("Kappa", 0.0)

                # Actualizamos estado
                item["Calibration_Status"] = "calibrated"
            else:
                # => Imagen NO aparece en .txt => uncalibrated
                item["Calibration_Status"] = "uncalibrated"
    
    # 3. Guardar el JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)
    
    print(f"JSON actualizado y guardado en: {json_output_path}")


def main():
    """
    Ejemplo de uso en línea de comandos:
    python step01_update_json.py ruta/datos.txt ruta/in.json ruta/out.json
    """
    import sys
    if len(sys.argv) < 4:
        print("Uso: python step01_update_json.py <archivo_calibracion.txt> <json_entrada> <json_salida>")
        sys.exit(1)
    
    txt_file = sys.argv[1]
    json_in  = sys.argv[2]
    json_out = sys.argv[3]
    
    # 1) Parsear el .txt
    calibration_dict = parse_calibration_txt(txt_file)
    
    # 2) Actualizar el JSON
    update_json_with_calibration(json_in, json_out, calibration_dict, image_identifier_key="ImageNumber")


if __name__ == "__main__":
    main()
