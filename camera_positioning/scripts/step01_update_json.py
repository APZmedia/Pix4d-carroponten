import json
import os

def parse_calibration_txt(txt_file_path):
    """
    Lee un archivo .txt que contiene datos de calibración para cada imagen.
    Se espera que la primera línea sea la cabecera:
    
        imageName  X   Y   Z   Omega   Phi   Kappa
    
    Retorna:
        dict con clave = Filename (str) y valor = {
            "X": float,
            "Y": float,
            "Z": float,
            "Omega": float,
            "Phi": float,
            "Kappa": float
        }
    """
    calibration_data = {}

    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    header = True  # Ignoramos la primera línea
    for line in lines:
        if header:
            header = False
            continue

        parts = line.strip().split()
        if len(parts) < 7:
            continue  # Aseguramos que hay suficientes columnas
        
        filename = parts[0].strip()  # Usamos el Filename completo como clave
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        omega = float(parts[4])
        phi   = float(parts[5])
        kappa = float(parts[6])

        calibration_data[filename] = {
            "X": x,
            "Y": y,
            "Z": z,
            "Omega": omega,
            "Phi": phi,
            "Kappa": kappa,
        }

    return calibration_data


def update_json_with_calibration(json_input_path, json_output_path, calibration_data):
    """
    Carga un JSON, actualiza coordenadas y orientación de imágenes calibradas
    usando 'Filename' como identificador.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    updated_count = 0
    missing_count = 0
    max_logs = 10  # Limitamos la cantidad de prints

    update_logs = []
    missing_logs = []

    for step_name, step_info in sequences_data.items():
        items = step_info.get("items", [])

        for item in items:
            filename = item.get("Filename", "").strip()  # Usamos Filename como clave

            if filename in calibration_data:
                cal_info = calibration_data[filename]

                if updated_count < max_logs:
                    update_logs.append(f"✅ {filename}: {cal_info}")

                item["X"] = cal_info["X"]
                item["Y"] = cal_info["Y"]
                item["Z"] = cal_info["Z"]
                item["Omega"] = cal_info["Omega"]
                item["Phi"]   = cal_info["Phi"]
                item["Kappa"] = cal_info["Kappa"]
                item["Calibration_Status"] = "calibrated"
                updated_count += 1
            else:
                if missing_count < max_logs:
                    missing_logs.append(f"❌ No en TXT: {filename}")
                item["Calibration_Status"] = "uncalibrated"
                missing_count += 1

    # 📌 Mostrar resumen en consola
    print("\n📌 **Primeros 10 valores actualizados:**")
    for log in update_logs[:max_logs]: 
        print(log)
    
    print("\n📌 **Últimos 10 valores actualizados:**")
    for log in update_logs[-max_logs:]: 
        print(log)

    print("\n⚠️ **Primeros 10 IDs que no fueron encontrados en TXT:**")
    for log in missing_logs[:max_logs]: 
        print(log)

    print(f"\n✅ Total imágenes actualizadas: {updated_count}")
    print(f"❌ Total imágenes NO encontradas en TXT: {missing_count}")

    # Guardar JSON actualizado
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)

    print(f"JSON actualizado en: {json_output_path}")


#############################################
# FUNCIÓN PRINCIPAL que llamarás desde main.py
#############################################
def run_step01(txt_path, json_in_path, json_out_path, image_identifier="ImageNumber"):
    """
    Ejecuta Step01: 
      1) Parsea el archivo .txt de calibración.
      2) Actualiza el JSON.
      3) Retorna un mensaje de estado final.
    """
    # 1) Parsear el .txt
    calibration_dict = parse_calibration_txt(txt_path)
    # 2) Actualizar el JSON
    update_json_with_calibration(
        json_in_path,
        json_out_path,
        calibration_dict
    )
    return f"✅ Step01 completado. Datos actualizados en {json_out_path}"


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
    update_json_with_calibration(json_in, json_out, calibration_dict)


if __name__ == "__main__":
    main()
