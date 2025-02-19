import math
from config import CENTER

def angle_to_xy(angle, radius, z=0):
    """Convert an angle and radius to (x, y, z) coordinates."""
    x = CENTER[0] + radius * math.cos(math.radians(angle))
    y = CENTER[1] + radius * math.sin(math.radians(angle))
    return [x, y, z]

def update_position_on_angle(new_angle, radius_value, pos):
    """Update (x, y) position while keeping z constant."""
    return angle_to_xy(new_angle, radius_value, pos[2] if len(pos) > 2 else 0)
