import json
import os
from pathlib import Path

# Ajusta este PATH al real donde tengas el JSON.
JSON_FILE_PATH = Path("data/ground_truth/all_sequences_clustered_updated.json")

def load_sequences_json(json_path=JSON_FILE_PATH):
    """
    Carga el JSON con estructura StepXX -> items -> [objetos de imagen].
    Devuelve un dict con dicha estructura.
    """
    if not json_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo {json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def save_sequences_json(data, json_path=JSON_FILE_PATH):
    """
    Guarda el dict (StepXX -> items -> [imagenes]) en el JSON conservando la estructura.
    """
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def update_image_status(all_data, calibrated_ids):
    """
    Marca como 'original' las imágenes cuyo ID esté en calibrated_ids.
    Marca como 'uncalibrated' el resto.
    """
    for step_name, step_info in all_data.items():
        for item in step_info["items"]:
            img_id_str = str(item.get("ImageNumber", ""))
            if img_id_str in calibrated_ids:
                item["Calibration_Status"] = "original"
            else:
                # Sólo si no está ya definida como 'original'
                # o si deseas forzar a 'uncalibrated' (depende de tu lógica).
                item["Calibration_Status"] = "uncalibrated"

def set_image_xyz(item, x, y, z):
    """
    Actualiza la posición X, Y, Z en el dict 'item'.
    """
    item["X"] = float(x)
    item["Y"] = float(y)
    item["Z"] = float(z)

def get_image_id_from_item(item):
    """
    Devuelve el ID (str) a partir del item. 
    """
    return str(item.get("ImageNumber", ""))

def find_item_by_id(all_data, image_id_str):
    """
    Retorna el dict de una imagen que tenga ImageNumber == image_id_str.
    Si no lo encuentra, retorna None.
    """
    for step_name, step_info in all_data.items():
        for item in step_info["items"]:
            if str(item.get("ImageNumber")) == image_id_str:
                return item
    return None
