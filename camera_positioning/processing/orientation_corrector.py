import math
import numpy as np

def normalize_angle_diff(diff):
    """
    Normaliza una diferencia angular en grados al rango [-180, 180).
    """
    return ((diff + 180) % 360) - 180

def infer_orientation_from_polar(image_item, center, sequence_items):
    """
    Calcula una orientación estimada (Kappa) basada en la posición polar respecto al centro de la grúa.
    Ajusta la orientación usando la diferencia promedio normalizada entre "Angular position" y Kappa
    en imágenes calibradas ("original").
    
    image_item: Diccionario con los datos de la imagen sin calibrar.
    center: Centro de la grúa en coordenadas [cx, cy].
    sequence_items: Lista de imágenes en la misma secuencia consideradas "original".
    
    Retorna el ángulo estimado en grados (Kappa estimado).
    """
    # 1️⃣ Calcular el ángulo polar de la imagen basado en su posición XY
    x = float(image_item.get("X", 0.0))
    y = float(image_item.get("Y", 0.0))
    cx = float(center[0])
    cy = float(center[1])
    dx, dy = x - cx, y - cy
    polar_angle = math.degrees(math.atan2(dy, dx)) % 360  # Rango 0-360

    # 2️⃣ Recolectar (Angular position, Kappa) de imágenes "original"
    calibrated_orientations = []
    for img in sequence_items:
        if img.get("Calibration_Status") == "original":
            theta = img.get("Angular position", None)
            kappa = img.get("Kappa", None)
            if theta is not None and kappa is not None:
                calibrated_orientations.append((float(theta), float(kappa)))
    
    # 3️⃣ Calcular la diferencia normalizada y obtener un offset promedio
    if calibrated_orientations:
        diffs = [normalize_angle_diff(kappa - theta) for theta, kappa in calibrated_orientations]
        avg_diff = np.median(diffs) if len(diffs) >= 3 else np.mean(diffs)
    else:
        avg_diff = 0.0

    # 4️⃣ Estimar Kappa: suma el offset promedio al ángulo polar
    estimated_kappa = (polar_angle + avg_diff) % 360
    return estimated_kappa
