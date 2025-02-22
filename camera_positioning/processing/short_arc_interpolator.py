import math
from data.json_handler import set_image_xyz

# Simple dict o CSV parseado. 
# La idea es: para un LandmarkID -> step01 -> un ID de imagen calibrada
VISUAL_MATCHES = {}  # Cargarlo si quieres, o parsear un CSV.

def interpolate_with_visual_matches(items_in_cluster, radius, center, step_name):
    """
    Cuando no hay calibradas, intentamos asignar un ángulo genérico 
    usando un ID calibrado parecido. 
    Este es un placeholder de ejemplo: 
    - Buscamos un Landmark en VISUAL_MATCHES que tenga step_name => un ID calibrado
    - Obtenemos su ángulo y lo asignamos a todas las imágenes del cluster.
    """
    # Chequea si tenemos un 'Landmark' con un ID calibrado en step_name
    matched_angle = None

    # EJEMPLO: recorre VISUAL_MATCHES y busca algo para step_name
    # Supongamos que VISUAL_MATCHES = {
    #   "Col02in": {"step01": "4323", "step02": "5052", ...}, ...
    # }
    for landmark, steps_map in VISUAL_MATCHES.items():
        if step_name in steps_map:
            # steps_map[step_name] es un ID calibrado => podemos obtener su ángulo
            # en la realidad, deberías buscar en tu all_data, item calibrado con ese ID
            # y calcular su ángulo.
            matched_angle = 100.0  # EJEMPLO HARDCODE
            break

    if matched_angle is None:
        # No hay referencia => no hacemos nada
        return

    # Asignamos a todas las imágenes en este cluster un XY basado en matched_angle
    for it in items_in_cluster:
        if it.get("Calibration_Status") != "original":
            # Asignar la misma X,Y => un anillo en un ángulo
            # Lógica de ejemplo: sumarle 1 grado por cada imagen para 'separarlas'
            idx = items_in_cluster.index(it)
            angle_used = matched_angle + idx
            set_item_xy_from_angle(it, angle_used, radius, center)
            it["Calibration_Status"] = "estimated"

def set_item_xy_from_angle(item, angle_deg, radius, center):
    """
    Calcula X,Y a partir de angle_deg y radius, conservando Z si existe. 
    """
    z_old = item.get("Z", 0.0)
    rad = math.radians(angle_deg)
    x_new = center[0] + radius * math.cos(rad)
    y_new = center[1] + radius * math.sin(rad)
    set_image_xyz(item, x_new, y_new, z_old)
