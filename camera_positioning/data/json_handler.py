import json
from pathlib import Path

# Define the path for the JSON data file
JSON_FILE_PATH = Path("/data/ground_truth/all_sequences.json")

def load_json():
    """Loads JSON data and ensures it follows the structured schema."""
    if not JSON_FILE_PATH.exists():
        raise FileNotFoundError(f"File {JSON_FILE_PATH} not found.")
    
    with open(JSON_FILE_PATH, "r", encoding="utf-8") as file:
        data = json.load(file)
    
    return transform_to_schema(data)

def save_json(data):
    """Saves JSON data in the standardized schema."""
    structured_data = transform_to_schema(data)
    with open(JSON_FILE_PATH, "w", encoding="utf-8") as file:
        json.dump(structured_data, file, indent=4)

def update_ground_truth(new_calibrated_data):
    """Updates the ground truth JSON with new calibrated camera positions."""
    ground_truth = load_json()
    calibrated_ids = set()
    
    for item in new_calibrated_data:
        calibrated_ids.add(item["Corrected_ID"])
        for entry in ground_truth:
            if entry["Corrected_ID"] == item["Corrected_ID"]:
                entry.update({
                    "camera_position_t": item["camera_position_t"],
                    "camera_rotation_R": item["camera_rotation_R"],
                    "corrected_camera_rotation_R": item["corrected_camera_rotation_R"],
                    "calibration_status": "original"
                })
    
    # Mark uncalibrated cameras
    for entry in ground_truth:
        if entry["Corrected_ID"] not in calibrated_ids:
            entry["calibration_status"] = "uncalibrated"
    
    save_json(ground_truth)

def transform_to_schema(sequence_data):
    """Transforms data into the required schema format."""
    transformed_data = []
    
    for sequence_id, sequence_info in sequence_data.items():
        for item in sequence_info.get("items", []):
            transformed_item = {
                "image": item["Filename"],
                "timestamp": item["Timestamp"],
                "image_width": item.get("image_width", 3840),
                "image_height": item.get("image_height", 5760),
                "camera_matrix_K": item.get("camera_matrix_K", [
                    [2212.9738650747, 0.0, 1921.9183142247],
                    [0.0, 2212.9738650747, 2876.3152586804],
                    [0.0, 0.0, 1.0]
                ]),
                "radial_distortion": item.get("radial_distortion", [-0.0158488321, 0.0127489656, -0.0027965167]),
                "tangential_distortion": item.get("tangential_distortion", [2.3399e-06, 0.0001324454]),
                "camera_position_t": item.get("camera_position_t", [0.0, 0.0, 0.0]),
                "camera_rotation_R": item.get("camera_rotation_R", [
                    [-0.4687159489, 0.8833480977, -0.0012237319],
                    [0.8828110672, 0.4683817577, -0.0355408027],
                    [-0.0308217268, -0.0177388652, -0.9993674769]
                ]),
                "calibration_status": item.get("calibration_status", "uncalibrated"),
                "SequenceID": sequence_id,
                "Corrected_ID": item["ImageNumber"],
                "corrected_camera_rotation_R": item.get("corrected_camera_rotation_R", [
                    [0.166125249, -0.9861046606, -0.0012237319],
                    [0.9861046606, 0.166125249, -0.0355408027],
                    [-0.0308217268, -0.0177388652, -0.9993674769]
                ]),
                "angle": item.get("angle", None)
            }
            transformed_data.append(transformed_item)
    
    return transformed_data
