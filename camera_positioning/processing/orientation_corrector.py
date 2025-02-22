import math
import numpy as np
from data.json_handler import find_item_by_id

def infer_orientation_from_polar(image_item, center, sequence_items):
    """
    Calcula una orientación estimada basada en la posición polar con respecto al centro.
    Se ajusta usando la orientación de imágenes calibradas dentro de la misma secuencia.

    image_item: Dict con la imagen no calibrada.
    center: Centro de la grúa en coordenadas [cx, cy].
    sequence_items: Lista de todas las imágenes en la secuencia actual.

    Retorna el ángulo estimado en grados (yaw/Kappa).
    """

    # 1. Calcular el ángulo en coordenadas polares
    x, y = image_item.get("X", 0.0), image_item.get("Y", 0.0)
    dx, dy = x - center[0], y - center[1]
    polar_angle = math.degrees(math.atan2(dy, dx))  # Angulo en coordenadas polares

    # 2. Buscar imágenes calibradas en la misma secuencia
    calibrated_orientations = []
    for img in sequence_items:
        if img.get("Calibration_Status") == "original":
            calibrated_orientations.append((img["computed_angle"], img["Kappa"]))

    # 3. Si hay imágenes calibradas, ajustar con la diferencia promedio
    if calibrated_orientations:
        diffs = []
        for cal_angle, cal_kappa in calibrated_orientations:
            diff = cal_kappa - cal_angle  # Diferencia entre la orientación real y el ángulo polar
            diffs.append(diff)
        
        if diffs:
            avg_diff = np.median(diffs)  # Tomamos la mediana para mayor estabilidad
        else:
            avg_diff = 0.0
    else:
        avg_diff = 0.0  # Si no hay calibradas, asumimos 0° de ajuste

    # 4. Aplicar corrección promedio
    estimated_kappa = (polar_angle + avg_diff) % 360

    return estimated_kappa  # Devolvemos la orientación corregida
