import numpy as np

# Global center point reference
CENTER = np.array([44.21328905, -29.13029399, 0])

# Hardcoded sequence radii
SEQUENCE_RADII = {
    "Step01": 49.464486,
    "Step02": 47.513978,
    "Step03": 42.515425,
}

# File paths (Modify as needed)
DATA_PATH = "examples/sample_data.json"
OUTPUT_PATH = "output/estimated_positions.json"
