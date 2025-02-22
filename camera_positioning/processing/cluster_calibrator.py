import math
import numpy as np
from collections import defaultdict
from data.json_handler import set_image_xyz
from processing.short_arc_interpolator import interpolate_with_visual_matches

def propagate_in_cluster(items_in_cluster, radius, center, step_name):
    """
    items_in_cluster: lista de diccionarios con las imágenes de un cluster.
    radius: radio calculado de la secuencia.
    center: np.array con [cx, cy, 0].
    step_name: 'Step01', 'Step02', etc.

    Lógica de ejemplo:
    1) Ordenar items por ImageNumber o Timestamp si lo tuvieras.
    2) Identificar calibradas (original) y no calibradas (uncalibrated).
    3) Interpolar ángulos y posiciones.
    """
    # Ordenar por ImageNumber (puedes usar Timestamp si te conviene)
    items_in_cluster.sort(key=lambda x: x["ImageNumber"])

    # Extraer calibradas
    calibradas = [it for it in items_in_cluster if it.get("Calibration_Status") == "original"]

    # Si tenemos al menos 2 calibradas, hacemos interpolación angular
    if len(calibradas) >= 2:
        # Calcular ángulos de cada calibrada
        for it in calibradas:
            # Si no tiene 'computed_angle', se lo calculamos a partir de X,Y
            if "computed_angle" not in it:
                it["computed_angle"] = compute_angle_from_xy(it["X"], it["Y"], center)
        # Recorremos items entre calibradas e interpolamos
        # Ejemplo: (calibradaA) ... (items uncalibrated) ... (calibradaB)
        # Repartimos linealmente la diferencia de ángulo
        for i in range(len(calibradas) - 1):
            idxA = items_in_cluster.index(calibradas[i])
            idxB = items_in_cluster.index(calibradas[i+1])
            angleA = calibradas[i]["computed_angle"]
            angleB = calibradas[i+1]["computed_angle"]
            n_interm = idxB - idxA - 1
            if n_interm > 0:
                delta = (angleB - angleA) / (n_interm + 1)
                for k in range(1, n_interm+1):
                    mid_item = items_in_cluster[idxA + k]
                    if mid_item.get("Calibration_Status") != "original":
                        mid_angle = angleA + delta * k
                        set_item_xy_from_angle(mid_item, mid_angle, radius, center)
                        mid_item["Calibration_Status"] = "estimated"
    else:
        # Caso: 0 ó 1 calibrada => fallback
        # Simplemente ajustamos con short_arc_interpolator o
        # con la lógica de Visual Matched IDs.
        interpolate_with_visual_matches(items_in_cluster, radius, center, step_name)

def compute_angle_from_xy(x, y, center):
    """
    Devuelve ángulo (grados) tal que angle=0 => (radius,0) con respecto a center.
    Usa atan2(dy, dx).
    """
    dx = x - center[0]
    dy = y - center[1]
    angle_rad = math.atan2(dy, dx)
    angle_deg = math.degrees(angle_rad)
    # Asegurar 0..360
    if angle_deg < 0:
        angle_deg += 360
    return angle_deg

def set_item_xy_from_angle(item, angle_deg, radius, center):
    """
    Calcula X,Y a partir de angle_deg y radius, y asigna a item.
    Mantiene Z si ya existe. 
    """
    z_old = item.get("Z", 0.0)
    rad = math.radians(angle_deg)
    x_new = center[0] + radius * math.cos(rad)
    y_new = center[1] + radius * math.sin(rad)
    set_image_xyz(item, x_new, y_new, z_old)

def calibrate_clusters_in_sequence(step_info, center):
    """
    Aplica propagate_in_cluster por cada cluster en step_info['items'].
    step_info: dict con "items", "calculated_radius", etc.
    """
    items = step_info.get("items", [])
    radius = step_info.get("calculated_radius", None)
    if not radius:
        # No hay radio => no hacemos nada
        return

    # Agrupar por cluster
    cluster_map = defaultdict(list)
    for it in items:
        c = it.get("Cluster", "NoCluster")
        cluster_map[c].append(it)
    
    for c_id, clist in cluster_map.items():
        propagate_in_cluster(clist, radius, center, step_info.get("StepName", ""))

def calibrate_all_sequences(all_data, center):
    """
    Recorre todos los StepXX y hace calibrate_clusters_in_sequence.
    """
    for step_name, step_info in all_data.items():
        # Guardamos el stepName dentro para reuso
        step_info["StepName"] = step_name
        calibrate_clusters_in_sequence(step_info, center)
    return all_data
