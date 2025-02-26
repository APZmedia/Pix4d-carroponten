import math
import numpy as np

def infer_orientation_from_polar(image_item, center, sequence_items):
    """
    Calcula una orientación estimada basada en la posición polar con respecto al centro de la grúa.
    Ajusta la orientación usando la diferencia promedio entre Theta y Kappa en imágenes calibradas.

    image_item: Diccionario con los datos de la imagen sin calibrar.
    center: Centro de la grúa en coordenadas [cx, cy].
    sequence_items: Lista de todas las imágenes en la misma secuencia.

    Retorna el ángulo estimado en grados (yaw/Kappa).
    """

    # 1️⃣ Calcular el ángulo en coordenadas polares basado en la posición XY
    x, y = image_item.get("X", 0.0), image_item.get("Y", 0.0)
    dx, dy = x - center[0], y - center[1]
    polar_angle = math.degrees(math.atan2(dy, dx)) % 360  # Convertimos a rango 0-360

    # 2️⃣ Buscar imágenes originales calibradas en la misma secuencia
    calibrated_orientations = []
    for img in sequence_items:
        if img.get("Calibration_Status") == "original":
            # Asegurar que existan datos para la calibración
            theta = img.get("Theta", None)
            kappa = img.get("Kappa", None)
            if theta is not None and kappa is not None:
                calibrated_orientations.append((theta, kappa))

    # 3️⃣ Si hay imágenes calibradas, calcular la diferencia media entre Theta y Kappa
    if calibrated_orientations:
        diffs = [kappa - theta for theta, kappa in calibrated_orientations]

        if len(diffs) >= 3:
            avg_diff = np.median(diffs)  # Mediana para evitar valores atípicos
        else:
            avg_diff = np.mean(diffs)  # Media si hay pocos datos
    else:
        avg_diff = 0.0  # Si no hay calibradas, asumimos sin corrección

    # 4️⃣ Aplicar corrección y asegurar continuidad de rotación
    estimated_kappa = (polar_angle + avg_diff) % 360

    return estimated_kappa  # Retornamos el valor corregido
