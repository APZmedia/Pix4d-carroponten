import numpy as np
import csv
from pathlib import Path

# Punto de referencia global (centro de la grúa)
CENTER = np.array([44.21328905, -29.13029399, 0])

# Ruta del archivo de Visual Match IDs
VISUAL_MATCH_IDS_FILE = Path("data/ground_truth/Visual match IDs to columns.csv")

def load_visual_match_ids():
    """
    Carga el CSV de 'Visual match IDs to columns.csv' y lo transforma en un diccionario.
    Retorna un diccionario con:
      { "LandmarkID": { "step01": ImageID, "step02": ImageID, ... }, ... }
    """
    visual_matches = {}
    
    if not VISUAL_MATCH_IDS_FILE.exists():
        print(f"⚠️ Archivo {VISUAL_MATCH_IDS_FILE} no encontrado. Ignorando Visual Match IDs.")
        return visual_matches  # Devuelve un diccionario vacío si el archivo no existe

    with open(VISUAL_MATCH_IDS_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            landmark_id = row["LandmarkID"].strip()
            visual_matches[landmark_id] = {
                step: row[step].strip() for step in row if step != "LandmarkID" and row[step].strip()
            }

    return visual_matches

# Cargar el archivo de visual match al inicio y almacenarlo en una variable global
VISUAL_MATCH_IDS = load_visual_match_ids()
