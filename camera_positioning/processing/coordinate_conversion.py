import numpy as np

def rotation_matrix_ypr(yaw, pitch, roll):
    """
    Calcula la matriz de rotación a partir de los ángulos Yaw-Pitch-Roll.
    """
    Rz = np.array([
        [np.cos(yaw), -np.sin(yaw), 0],
        [np.sin(yaw), np.cos(yaw), 0],
        [0, 0, 1]
    ])
    
    Ry = np.array([
        [np.cos(pitch), 0, np.sin(pitch)],
        [0, 1, 0],
        [-np.sin(pitch), 0, np.cos(pitch)]
    ])
    
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(roll), -np.sin(roll)],
        [0, np.sin(roll), np.cos(roll)]
    ])
    
    return Rz @ Ry @ Rx

def rotation_matrix_opk(omega, phi, kappa):
    """
    Calcula la matriz de rotación a partir de los ángulos Omega-Phi-Kappa.
    """
    Rx = np.array([
        [1, 0, 0],
        [0, np.cos(omega), -np.sin(omega)],
        [0, np.sin(omega), np.cos(omega)]
    ])
    
    Ry = np.array([
        [np.cos(phi), 0, np.sin(phi)],
        [0, 1, 0],
        [-np.sin(phi), 0, np.cos(phi)]
    ])
    
    Rz = np.array([
        [np.cos(kappa), -np.sin(kappa), 0],
        [np.sin(kappa), np.cos(kappa), 0],
        [0, 0, 1]
    ])
    
    return Rx @ Ry @ Rz

def ypr_to_opk(yaw, pitch, roll):
    """
    Convierte los ángulos YPR a OPK.
    """
    R_ypr = rotation_matrix_ypr(yaw, pitch, roll)
    omega = np.arctan2(R_ypr[2,1], R_ypr[2,2])
    phi = np.arcsin(-R_ypr[2,0])
    kappa = np.arctan2(R_ypr[1,0], R_ypr[0,0])
    
    return omega, phi, kappa

def opk_to_ypr(omega, phi, kappa):
    """
    Convierte los ángulos OPK a YPR.
    """
    R_opk = rotation_matrix_opk(omega, phi, kappa)
    yaw = np.arctan2(R_opk[1,0], R_opk[0,0])
    pitch = np.arcsin(-R_opk[2,0])
    roll = np.arctan2(R_opk[2,1], R_opk[2,2])
    
    return yaw, pitch, roll
