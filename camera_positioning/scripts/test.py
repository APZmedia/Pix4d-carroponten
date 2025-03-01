import math
import numpy as np
import matplotlib.pyplot as plt

def build_local_frame(cx, cy, x_cam, y_cam):
    """
    Construye la matriz base (3x3) para el sistema local.
    - x_local: vector radial (desde el centro (cx,cy) hacia la posición de la cámara (x_cam,y_cam))
    - y_local: vector tangencial (rotado 90° antihorario de x_local)
    - z_local: vertical (0,0,1)
    """
    vx = x_cam - cx
    vy = y_cam - cy
    norm_xy = math.hypot(vx, vy)
    if norm_xy < 1e-9:
        return np.eye(3)
    radial = np.array([vx / norm_xy, vy / norm_xy, 0.0])
    tang = np.array([-radial[1], radial[0], 0.0])  # rotación 90° antihorario
    vert = np.array([0, 0, 1], dtype=float)
    Rbase = np.column_stack((radial, tang, vert))
    return Rbase

def angles_to_rotation_matrix(omega_deg, phi_deg, kappa_deg):
    """
    Convierte (omega, phi, kappa) en grados a una matriz de rotación 3x3.
    Se usa la convención: R = Rx(omega) * Ry(phi) * Rz(kappa)
    """
    om = math.radians(omega_deg)
    ph = math.radians(phi_deg)
    kp = math.radians(kappa_deg)
    
    Rx = np.array([
        [1, 0, 0],
        [0, math.cos(om), -math.sin(om)],
        [0, math.sin(om), math.cos(om)]
    ], dtype=float)
    
    Ry = np.array([
        [math.cos(ph), 0, math.sin(ph)],
        [0, 1, 0],
        [-math.sin(ph), 0, math.cos(ph)]
    ], dtype=float)
    
    Rz = np.array([
        [math.cos(kp), -math.sin(kp), 0],
        [math.sin(kp), math.cos(kp), 0],
        [0, 0, 1]
    ], dtype=float)
    
    return Rx @ Ry @ Rz

def rotation_matrix_to_angles(R):
    """
    Extrae (omega, phi, kappa) en grados de una matriz de rotación 3x3
    usando la convención:
      omega = arctan2(R[2,1], R[2,2])
      phi   = arcsin(R[0,2])
      kappa = arctan2(R[0,1], R[0,0])
    """
    omega = math.atan2(R[2,1], R[2,2])
    phi = math.asin(R[0,2])
    kappa = math.atan2(R[0,1], R[0,0])
    return (math.degrees(omega), math.degrees(phi), math.degrees(kappa))

def local_to_global_opk(omega_l, phi_l, kappa_l, cx, cy, x_cam, y_cam):
    """
    Convierte la orientación local (omega_l, phi_l, kappa_l) a orientación global,
    usando la base local definida por el centro (cx,cy) y la posición de la cámara (x_cam,y_cam).
    """
    Rlocal = angles_to_rotation_matrix(omega_l, phi_l, kappa_l)
    Rbase = build_local_frame(cx, cy, x_cam, y_cam)
    Rglobal = Rbase @ Rlocal
    return rotation_matrix_to_angles(Rglobal)

# --- Simulación ---
# Definiciones
center = (0.0, 0.0)    # Centro del círculo
radius = 10.0          # Radio del círculo

# Orientación local constante para la cámara.
# En el sistema local se asume:
#   omega_local (roll) = 5°
#   phi_local   (pitch) = 2°
#   kappa_local (yaw local) = 0° (apunta exactamente tangencialmente)
local_orientation = (5.0, 2.0, 0.0)

# Listas para almacenar resultados
thetas = np.arange(0, 361, 5)
omega_globals = []
phi_globals = []
kappa_globals = []

# Simulación: para cada ángulo de posición θ se calcula la orientación global
for theta in thetas:
    theta_rad = math.radians(theta)
    # Posición de la cámara en el círculo
    x_cam = center[0] + radius * math.cos(theta_rad)
    y_cam = center[1] + radius * math.sin(theta_rad)
    
    # Convertir la orientación local constante a global para esta posición
    omega_g, phi_g, kappa_g = local_to_global_opk(
        local_orientation[0],
        local_orientation[1],
        local_orientation[2],
        center[0], center[1],
        x_cam, y_cam
    )
    
    omega_globals.append(omega_g)
    phi_globals.append(phi_g)
    kappa_globals.append(kappa_g)

# Graficar los resultados
plt.figure(figsize=(10, 6))
plt.plot(thetas, omega_globals, label='Omega_global', marker='o')
plt.plot(thetas, phi_globals, label='Phi_global', marker='o')
plt.plot(thetas, kappa_globals, label='Kappa_global', marker='o')
plt.xlabel("θ (deg)")
plt.ylabel("Ángulos globales (deg)")
plt.title("Simulación: Orientación global vs. θ en un círculo")
plt.legend()
plt.grid(True)
plt.show()
