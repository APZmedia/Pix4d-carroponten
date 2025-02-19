import json
from data.json_handler import load_json, save_json
from processing.cluster_calibrator import calibrate_clusters
from processing.short_arc_interpolator import short_arc_interpolation
from utils.constants import JSON_FILE_PATH, CENTER

def calibrate_clusters_job():
    """Runs the cluster calibration process."""
    try:
        records = load_json(JSON_FILE_PATH)
        calibrated_records = calibrate_clusters(records)
        save_json(JSON_FILE_PATH, calibrated_records)
        return f"Calibration complete. Records saved to '{JSON_FILE_PATH}'."
    except Exception as e:
        return f"Error during calibration: {e}"

def interpolate_positions_job():
    """Interpolates uncalibrated positions using short-arc interpolation."""
    try:
        records = load_json(JSON_FILE_PATH)
        calibrated_positions = {str(rec["Corrected_ID"]): rec["camera_position_t"][:2] for rec in records if rec.get("calibration_status") == "original"}
        uncalibrated_positions = {str(rec["Corrected_ID"]): rec["camera_position_t"][:2] for rec in records if rec.get("calibration_status") != "original"}

        updated_data, adjusted_positions = short_arc_interpolation(
            records, calibrated_positions, uncalibrated_positions, CENTER[0], CENTER[1]
        )
        save_json(JSON_FILE_PATH, updated_data)
        return f"Interpolation complete. Adjusted {len(adjusted_positions)} positions."
    except Exception as e:
        return f"Error during interpolation: {e}"
