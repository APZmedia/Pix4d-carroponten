import json
from pathlib import Path

# Define paths
GROUND_TRUTH_PATH = Path("ground_truth/all_sequences.json")
NEW_CALIBRATED_DATA_PATH = Path("input/new_calibrated_data.json")
OUTPUT_PATH = Path("output/updated_all_sequences.json")

def load_json(file_path):
    """Loads JSON data from a file."""
    if not file_path.exists():
        raise FileNotFoundError(f"File {file_path} not found.")
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

def save_json(data, file_path):
    """Saves JSON data to a file."""
    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)

def update_ground_truth(new_calibrated_data):
    """Updates the ground truth JSON with new calibrated camera positions."""
    ground_truth = load_json(GROUND_TRUTH_PATH)
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
    
    return ground_truth

def main():
    """Loads new calibrated data, updates the ground truth, and saves the updated JSON."""
    print("Loading new calibrated data...")
    new_calibrated_data = load_json(NEW_CALIBRATED_DATA_PATH)
    
    print("Updating ground truth...")
    updated_data = update_ground_truth(new_calibrated_data)
    
    print(f"Saving updated data to {OUTPUT_PATH}...")
    save_json(updated_data, OUTPUT_PATH)
    
    print("Update complete!")

if __name__ == "__main__":
    main()
