import numpy as np

def compute_orientation_offset(calibrated_images):
    """Computes median orientation offset."""
    offsets = np.array([img["true_orientation"] - img["computed_angle"] for img in calibrated_images])
    return np.median(offsets) if len(offsets) > 0 else 0

def apply_orientation_correction(estimated_angle, offset):
    """Applies offset to an estimated angle, keeping it in [0, 360) degrees."""
    return (estimated_angle + offset) % 360
