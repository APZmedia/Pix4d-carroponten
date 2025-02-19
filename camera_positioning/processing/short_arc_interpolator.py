from data.sequence_handler import get_image_info

def short_arc_interpolation(data, calibrated_positions, uncalibrated_positions, center_x, center_y):
    """Adjusts uncalibrated positions using short-arc interpolation."""
    
    updated_positions = {}

    # Process each uncalibrated entry
    for image_number, position in uncalibrated_positions.items():
        image_info = get_image_info(int(image_number))
        
        if not image_info:
            continue  # Skip if no ground truth data
        
        filename = image_info["Filename"]
        timestamp = image_info["Timestamp"]
        sequence = image_info["Sequence"]
        
        # Interpolate the position (Example logic)
        interpolated_x = center_x + 0.5  # Placeholder logic
        interpolated_y = center_y + 0.5  # Placeholder logic
        
        updated_positions[image_number] = [interpolated_x, interpolated_y]
        
        # Update JSON directly
        for entry in data:
            if str(entry.get("Corrected_ID")) == str(image_number):
                entry["camera_position_t"] = [float(interpolated_x), float(interpolated_y)]
                entry["Filename"] = filename
                entry["Timestamp"] = timestamp
                entry["Sequence"] = sequence
                break  # Stop searching once the entry is found

    return data, updated_positions
