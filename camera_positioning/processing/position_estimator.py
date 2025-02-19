import numpy as np
from datetime import datetime
from data.json_handler import load_json, save_json
from config import CENTER

def calculate_sequence_radius(cameras):
    """Computes the median radius for a given sequence."""
    positions = np.array([np.linalg.norm(np.array(cam["camera_position_t"]) - CENTER) for cam in cameras])
    return np.median(positions) if len(positions) else 0

def estimate_positions(camera_data):
    """Estimates missing camera positions."""
    sequence_groups = {}
    sequence_radii = {}

    # Group by ID
    for cam in camera_data:
        seq_id = cam["ID"]
        sequence_groups.setdefault(seq_id, []).append(cam)

    # Calculate median radius per sequence
    for seq_id, cameras in sequence_groups.items():
        sequence_radii[seq_id] = calculate_sequence_radius(cameras)

    for seq_id, cameras in sequence_groups.items():
        cameras.sort(key=lambda x: datetime.strptime(x["timestamp"], "%Y:%m:%d %H:%M:%S"))
        timestamps = np.array([datetime.strptime(cam["timestamp"], "%Y:%m:%d %H:%M:%S") for cam in cameras])
        positions = np.array([cam["camera_position_t"] for cam in cameras])

        calibrated_idxs = [i for i, cam in enumerate(cameras) if cam["Estimated_Confidence"] == "original"]
        
        if len(calibrated_idxs) < 2:
            continue  # Skip sequences with insufficient calibration points

        avg_speed = np.mean(np.diff(positions[calibrated_idxs], axis=0), axis=0)
        avg_angle = np.mean(np.arctan2(positions[calibrated_idxs][1:, 1] - positions[calibrated_idxs][:-1, 1],
                                       positions[calibrated_idxs][1:, 0] - positions[calibrated_idxs][:-1, 0]))

        for i, cam in enumerate(cameras):
            if cam["Estimated_Confidence"] != "original":
                prev_idx = max([idx for idx in calibrated_idxs if idx < i], default=None)
                next_idx = min([idx for idx in calibrated_idxs if idx > i], default=None)

                if prev_idx is not None:
                    dt = (timestamps[i] - timestamps[prev_idx]).total_seconds()
                    cam["camera_position_t"][:2] = positions[prev_idx][:2] + avg_speed * dt
                    cam["Estimated_Confidence"] = "timestamp-based"

    return camera_data
