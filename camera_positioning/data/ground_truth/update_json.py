import json

# Definir los nuevos campos con valores por defecto
NEW_FIELDS = {
    "camera_matrix_K": [
        [2212.9738650747, 0.0, 1921.9183142247],
        [0.0, 2212.9738650747, 2876.3152586804],
        [0.0, 0.0, 1.0]
    ],
    "radial_distortion": [-0.0158488321, 0.0127489656, -0.0027965167],
    "tangential_distortion": [2.3399e-06, 0.0001324454],
    "camera_position_t": [3.45, -1.11, 5.623628],
    "camera_rotation_R": [
        [-0.4687159489, 0.8833480977, -0.0012237319],
        [0.8828110672, 0.4683817577, -0.0355408027],
        [-0.0308217268, -0.0177388652, -0.9993674769]
    ],
    "corrected_camera_rotation_R": [
        [0.166125249, -0.9861046606, -0.0012237319],
        [0.9861046606, 0.166125249, -0.0355408027],
        [-0.0308217268, -0.0177388652, -0.9993674769]
    ],
    "computed_angle": 145.49574096861363,
    "corrected_angle": 145.49574096861363,
    "Calibration_Status": "original",
    "previous": "",
    "next": ""
}

# Cargar el archivo JSON original
input_filename = r"D:\Pix4d-carroponten\camera_positioning\data\ground_truth\all_sequences_updated.json"
output_filename = r"D:\Pix4d-carroponten\camera_positioning\data\ground_truth\all_sequences_clustered_updated.json"

try:
    with open(input_filename, "r", encoding="utf-8") as file:
        data = json.load(file)
except FileNotFoundError:
    print(f"Error: No se encontró el archivo '{input_filename}'.")
    exit(1)

# Iterar sobre cada secuencia en el JSON
for step, step_data in data.items():
    if "items" in step_data:
        items = step_data["items"]
        
        # Recorrer cada imagen en la lista
        for i, image in enumerate(items):
            # Agregar campos nuevos si no existen
            for key, value in NEW_FIELDS.items():
                if key not in image:
                    image[key] = value
            
            # Agregar referencias de imágenes previas y siguientes
            image["previous"] = items[i - 1]["Filename"] if i > 0 else ""
            image["next"] = items[i + 1]["Filename"] if i < len(items) - 1 else ""

# Guardar el JSON actualizado
with open(output_filename, "w", encoding="utf-8") as file:
    json.dump(data, file, indent=4, ensure_ascii=False)

print(f"JSON actualizado guardado en '{output_filename}'.")
