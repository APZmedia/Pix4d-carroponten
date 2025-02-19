import json
from pathlib import Path

GROUND_TRUTH_PATH = Path("data/ground_truth/all_sequences.json")

def load_ground_truth():
    """Loads the all_sequences.json file and structures the data."""
    with open(GROUND_TRUTH_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    sequence_map = {}
    image_map = {}

    # Process all sequences
    for sequence, details in data.items():
        items = details.get("items", [])
        sequence_map[sequence] = {
            "axis_center": details.get("axis_center", {}),
            "calculated_radius": details.get("calculated_radius", 0),
            "start": details.get("start"),
            "end": details.get("end"),
            "items": items
        }

        # Map images to their filenames and timestamps
        for item in items:
            image_map[item["ImageNumber"]] = {
                "Filename": item["Filename"],
                "Timestamp": item["Timestamp"],
                "Sequence": item["Sequence"]
            }

    return sequence_map, image_map

SEQUENCES, IMAGE_MAP = load_ground_truth()

def get_sequence_info(sequence_id):
    """Retrieves sequence details."""
    return SEQUENCES.get(sequence_id, {})

def get_image_info(image_number):
    """Retrieves image filename and timestamp based on ImageNumber."""
    return IMAGE_MAP.get(image_number, {})
