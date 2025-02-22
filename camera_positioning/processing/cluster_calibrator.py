import math
import numpy as np
from collections import defaultdict
from data.json_handler import set_image_xyz
from processing.orientation_corrector import infer_orientation_from_polar
from config import CENTER

def propagate_positions_in_cluster(items_in_cluster, center, radius):
    """
    Propaga posiciones en un cluster basado en imágenes calibradas cercanas.
    Como todas las imágenes en la secuencia tienen el mismo radio, 
    solo ajustamos los ángulos polares para interpolar posiciones.
    """
    items_in_cluster.sort(key=lambda x: x["ImageNumber"])  # Orden por imagen

    # Extraemos imágenes calibradas
    calibrated = [it for it in items_in_cluster if it.get("Calibration_Status") == "original"]

    # Si hay al menos dos calibradas, interpolamos posiciones angulares
    if len(calibrated) >= 2:
        for i in range(len(calibrated) - 1):
            idxA = items_in_cluster.index(calibrated[i])
            idxB = items_in_cluster.index(calibrated[i+1])
            angleA = math.degrees(math.atan2(calibrated[i]["Y"] - center[1], calibrated[i]["X"] - center[0]))
            angleB = math.degrees(math.atan2(calibrated[i+1]["Y"] - center[1], calibrated[i+1]["X"] - center[0]))
            n_interm = idxB - idxA - 1
            
            if n_interm > 0:
                delta_angle = (angleB - angleA) / (n_interm + 1)
                for k in range(1, n_interm+1):
                    mid_item = items_in_cluster[idxA + k]
                    if mid_item.get("Calibration_Status") != "original":
                        interpolated_angle = angleA + delta_angle * k
                        rad = math.radians(interpolated_angle)
                        new_x = center[0] + radius * math.cos(rad)
                        new_y = center[1] + radius * math.sin(rad)
                        set_image_xyz(mid_item, new_x, new_y, mid_item["Z"])
                        mid_item["Calibration_Status"] = "estimated"

def propagate_orientations_in_cluster(sequence_items, center):
    """
    Infere la orientación de imágenes sin calibrar dentro de un cluster usando coordenadas polares.
    Si no hay calibraciones, usa interpolación angular.
    """
    calibrated_orientations = []
    for img in sequence_items:
        if img.get("Calibration_Status") == "original":
            angle = math.degrees(math.atan2(img["Y"] - center[1], img["X"] - center[0]))
            calibrated_orientations.append((angle, img["Kappa"]))

    for item in sequence_items:
        if item.get("Calibration_Status") == "uncalibrated":
            estimated_kappa = infer_orientation_from_polar(item, center, sequence_items, calibrated_orientations)
            item["Kappa"] = estimated_kappa
            item["Calibration_Status"] = "estimated"

def calibrate_clusters_in_sequence(step_info, center):
    """
    Procesa cada cluster dentro de una secuencia, propagando posiciones y orientación.
    """
    items = step_info.get("items", [])
    radius = step_info.get("calculated_radius", None)
    
    if not radius:
        return  # No hay radio definido, no podemos calcular bien

    # Agrupar por cluster
    cluster_map = defaultdict(list)
    for it in items:
        cluster_map[it.get("Cluster", "NoCluster")].append(it)
    
    for cluster_id, clist in cluster_map.items():
        propagate_positions_in_cluster(clist, center, radius)
        propagate_orientations_in_cluster(clist, center)

def calibrate_all_sequences(all_data, center):
    """
    Recorre todos los StepXX y ejecuta la calibración por cluster.
    """
    for step_name, step_info in all_data.items():
        step_info["StepName"] = step_name
        calibrate_clusters_in_sequence(step_info, center)
    return all_data
