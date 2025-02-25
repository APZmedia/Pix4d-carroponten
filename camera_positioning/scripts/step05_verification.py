import json
import numpy as np
import plotly.graph_objects as go

def get_common_axis_limits(*data_arrays):
    """
    Obtiene los límites comunes para los ejes X e Y basados en múltiples listas de coordenadas.
    """
    valid_x = [x for x_list in data_arrays[::2] for x in x_list if x is not None]
    valid_y = [y for y_list in data_arrays[1::2] for y in y_list if y is not None]

    if not valid_x or not valid_y:
        return None, None, None, None  # Evita errores si no hay datos

    return min(valid_x), max(valid_x), min(valid_y), max(valid_y)


def run_step05_verification(json_file_path, txt_file_path):
    """
    Genera gráficos comparando:
    - Posiciones originales (TXT).
    - Posiciones visualmente calibradas, interpoladas y originales (JSON).
    """
    # 📌 Leer JSON con nuevas posiciones
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # Listas de coordenadas para los diferentes estados de calibración
    json_x_calib, json_y_calib = [], []
    json_x_interp, json_y_interp = [], []
    json_x_original, json_y_original = [], []

    for step_name, step_info in json_data.items():
        for item in step_info.get("items", []):
            if "X" in item and "Y" in item and item["X"] is not None and item["Y"] is not None:
                status = item.get("Calibration_Status", "").lower()
                if status == "visually calibrated":
                    json_x_calib.append(item["X"])
                    json_y_calib.append(item["Y"])
                elif status == "estimated":
                    json_x_interp.append(item["X"])
                    json_y_interp.append(item["Y"])
                elif status == "original":
                    json_x_original.append(item["X"])
                    json_y_original.append(item["Y"])

    # 📌 Leer TXT original
    txt_x, txt_y = [], []
    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:  # Saltamos la cabecera
        parts = line.strip().split()
        if len(parts) >= 3:
            try:
                txt_x.append(float(parts[1]))  # X
                txt_y.append(float(parts[2]))  # Y
            except ValueError:
                continue  # Manejo de errores en caso de valores inválidos

    # 📌 Obtener límites comunes para ambos gráficos
    x_min, x_max, y_min, y_max = get_common_axis_limits(
        json_x_calib, json_y_calib,
        json_x_interp, json_y_interp,
        json_x_original, json_y_original,
        txt_x, txt_y
    )

    # 📌 Si no hay datos válidos, evitar errores en la escala
    if None in (x_min, x_max, y_min, y_max):
        x_min, x_max, y_min, y_max = -50, 50, -50, 50  # Rango por defecto si no hay datos

    # 📌 Crear gráfico TXT original
    fig_txt = go.Figure()
    if txt_x and txt_y:
        fig_txt.add_trace(go.Scatter(x=txt_x, y=txt_y, mode="markers", marker=dict(color="green"), name="TXT Original"))
    fig_txt.update_layout(
        title="Posiciones Originales (TXT)",
        xaxis=dict(title="X", range=[x_min, x_max]),
        yaxis=dict(title="Y", range=[y_min, y_max]),
        width=600, height=500
    )

    # 📌 Crear gráfico JSON con nuevas posiciones
    fig_json = go.Figure()
    if json_x_calib and json_y_calib:
        fig_json.add_trace(go.Scatter(x=json_x_calib, y=json_y_calib, mode="markers", marker=dict(color="blue"), name="Visually Calibrated"))
    if json_x_interp and json_y_interp:
        fig_json.add_trace(go.Scatter(x=json_x_interp, y=json_y_interp, mode="markers", marker=dict(color="red"), name="Interpolated"))
    if json_x_original and json_y_original:
        fig_json.add_trace(go.Scatter(x=json_x_original, y=json_y_original, mode="markers", marker=dict(color="orange"), name="Original"))

    fig_json.update_layout(
        title="Posiciones Visualmente Calibradas, Interpoladas y Originales",
        xaxis=dict(title="X", range=[x_min, x_max]),
        yaxis=dict(title="Y", range=[y_min, y_max]),
        width=600, height=500
    )

    # 📌 Mensajes de depuración
    print(f"✅ Total imágenes 'Original': {len(json_x_original)}")
    print(f"🔵 Total 'Visually Calibrated': {len(json_x_calib)}")
    print(f"🔴 Total 'Interpolated': {len(json_x_interp)}")
    print(f"🟢 Total 'TXT Original': {len(txt_x)}")

    return fig_txt, fig_json
