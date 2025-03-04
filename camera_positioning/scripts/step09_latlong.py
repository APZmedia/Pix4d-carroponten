import json
import csv
import math
import gradio as gr
from pathlib import Path

def xy_to_latlon(x, y, center_lat, center_lon, scale_factor):
    """
    Convierte coordenadas locales X, Y a latitud y longitud usando un factor de escala dinámico.
    """
    lat = center_lat + (y * scale_factor)  # Ajuste de Norte-Sur
    lon = center_lon + (x * scale_factor)  # Ajuste de Este-Oeste
    return lat, lon

def estimate_scale_factor(radius_meters, reference_degree=111000):
    """
    Estima el factor de conversión de metros a grados con base en el radio promedio.
    """
    return radius_meters / reference_degree if radius_meters else 0.00001

def add_latlon_to_json(json_input_path, json_output_path, center_lat, center_lon):
    """
    Agrega latitud y longitud a cada imagen en el JSON considerando su eje central y radio.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)
    
    for step_name, step_info in sequences_data.items():
        axis_center = step_info.get("axis_center", {"x": 0.0, "y": 0.0})
        radius = step_info.get("calculated_radius", 1.0)  # Evitar división por cero
        scale_factor = estimate_scale_factor(radius)
        
        for item in step_info.get("items", []):
            if "camera_position_t" in item:
                x, y = item["camera_position_t"][:2]  # Extraer X, Y
                lat, lon = xy_to_latlon(x, y, center_lat, center_lon, scale_factor)
                item["Latitude"] = lat
                item["Longitude"] = lon
    
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)
    
    print(f"✅ Latitudes y longitudes agregadas. Guardado en {json_output_path}")

def export_csv_with_latlon(json_input_path, csv_output_path):
    """
    Exporta un CSV en formato Pix4D con coordenadas geográficas.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)
    
    with open(csv_output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert", "Latitude", "Longitude"])
        
        for step_name, step_info in sequences_data.items():
            for item in step_info.get("items", []):
                writer.writerow([
                    item.get("Filename", "Unknown"),
                    item["camera_position_t"][0] if "camera_position_t" in item else 0.0,
                    item["camera_position_t"][1] if "camera_position_t" in item else 0.0,
                    item["camera_position_t"][2] if "camera_position_t" in item else 0.0,
                    item.get("Omega", 0.0),
                    item.get("Phi", 0.0),
                    item.get("Kappa", 0.0),
                    1.0,  # SigmaHoriz ajustado
                    0.3,  # SigmaVert ajustado
                    item.get("Latitude", 0.0),
                    item.get("Longitude", 0.0)
                ])
    
    print(f"✅ CSV con coordenadas geográficas exportado en {csv_output_path}")