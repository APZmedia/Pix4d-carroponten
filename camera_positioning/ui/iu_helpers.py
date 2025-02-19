import numpy as np
from processing.orientation_corrector import compute_suggested_next_angle, calculate_max_angular_correction
from processing.angular_transform import update_position_on_angle
from data.json_handler import load_json, save_json
from config import JSON_FILE_PATH, CENTER

def process_toggle(show, prev_angle, next_angle):
    """Toggles the visibility of adjacent angles."""
    return (str(prev_angle), str(next_angle)) if show else ("", "")

def compute_suggestion(curr_image_input, next_image_input, curr_pos, cluster_current, next_delta, analyzer):
    """Computes the suggested next angle based on pixel shifts."""
    current_record = {"camera_position_t": curr_pos, "SequenceID": cluster_current}
    calibration_params = (0.5, 0.1)
    max_speed_deg_per_sec = 5.0
    max_angular_correction = calculate_max_angular_correction(next_delta, max_speed_deg_per_sec)
    
    try:
        current_angle, suggested_next_angle, computed_correction, clamped_correction, mean_shift = compute_suggested_next_angle(
            curr_image_input, next_image_input, current_record, calibration_params, analyzer, max_angular_correction
        )
        return (
            f"{current_angle:.2f}°",
            f"{suggested_next_angle:.2f}°",
            f"{computed_correction:.2f}°",
            f"{clamped_correction:.2f}°",
            f"{mean_shift:.2f} pixels"
        )
    except Exception as e:
        return ("Error", "Error", "Error", "Error", str(e))

def save_json_data(data):
    """Saves updated JSON data."""
    save_json(JSON_FILE_PATH, data)
    return f"Data saved to {JSON_FILE_PATH}"
