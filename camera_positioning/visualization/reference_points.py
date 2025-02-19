import numpy as np

REFERENCE_POINTS_DATA = """
Col07in,73.7131947562057,-32.7452436102905,5.23201128448096
Col09in,70.7254261175117,-42.6052848805698,5.21665888768214
Col10in,67.9464074026829,-46.9908383346911,5.2151058514766
Col08in,72.6320457036271,-37.8467250575676,5.20638561843738
"""

def parse_reference_points(data_str):
    """Parses reference points from a comma-separated string."""
    reference_dict = {}
    lines = data_str.strip().split('\n')
    for line in lines:
        parts = line.split(',')
        if len(parts) < 4:
            continue
        name = parts[0].strip()
        x = float(parts[1])
        y = float(parts[2])
        z = float(parts[3])
        reference_dict[name] = np.array([x, y, z])
    return reference_dict

# Load reference points once
REFERENCE_POINTS = parse_reference_points(REFERENCE_POINTS_DATA)
