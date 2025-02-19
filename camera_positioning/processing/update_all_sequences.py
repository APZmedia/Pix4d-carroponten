import json
import shutil
from pathlib import Path
from data.json_handler import load_json, save_json

# Define file paths
GROUND_TRUTH_PATH = Path("ground_truth/all_sequences.json")
BACKUP_PATH = Path("ground_truth/all_sequences_backup.json")

def parse_txt_file(txt_file):
    """Parses the calibration .txt file and extracts camera parameters."""
    with open(txt_file, "r", encoding="utf-8") as file:
        lines = file.readlines()

    cameras = {}
    for line in lines:
        parts = line.strip().split()
        if len(parts) >= 9:  # Ensure there are enough elements
            file_name = parts[0]  # Image filename
            camera_position_t = list(map(float, parts[1:4]))  # X, Y, Z
            camera_rotation_R = list(map(float, parts[4:7]))  # Omega, Phi, Kappa

            cameras[file_name] = {
                "camera_position_t": camera_position_t,
                "camera_rotation_R": camera_rotation_R,
                "calibration_status": "original",
            }
    return cameras

def update_all_sequences(txt_file):
    """Updates `all_sequences.json` with new calibrated positions & orientations, without modifying other fields."""
    txt_file = Path(txt_file)
    if not txt_file.exists():
        print(f"Error: {txt_file} not found.")
        return
    
    if not GROUND_TRUTH_PATH.exists():
        print("Error: all_sequences.json not found.")
        return

    # Create a backup before modifying
    shutil.copy(GROUND_TRUTH_PATH, BACKUP_PATH)
    print(f"Backup of all_sequences.json saved to {BACKUP_PATH}")

    ground_truth = load_json(GROUND_TRUTH_PATH)
    new_data = parse_txt_file(txt_file)
    calibrated_ids = set()

    # Step 1: Update calibrated images
    for entry in ground_truth:
        image_name = entry.get("image")
        if image_name in new_data:
            entry["camera_position_t"] = new_data[image_name]["camera_position_t"]
            entry["camera_rotation_R"] = new_data[image_name]["camera_rotation_R"]
            entry["calibration_status"] = "original"
            calibrated_ids.add(entry["Corrected_ID"])
    
    # Step 2: Mark all other entries as "uncalibrated"
    for entry in ground_truth:
        if entry["Corrected_ID"] not in calibrated_ids:
            entry["calibration_status"] = "uncalibrated"

    save_json(ground_truth, GROUND_TRUTH_PATH)
    print(f"Updated {len(calibrated_ids)} entries in all_sequences.json.")
    print(f"Uncalibrated images marked appropriately.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Update all_sequences.json with calibrated camera parameters.")
    parser.add_argument("txt_file", type=str, help="Path to the calibration .txt file")
    args = parser.parse_args()
    update_all_sequences(args.txt_file)
