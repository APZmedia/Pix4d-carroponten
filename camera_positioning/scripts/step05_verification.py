import json
import plotly.graph_objects as go

def get_common_axis_limits(x1, y1, x2, y2):
    """
    Obtiene los límites comunes para los ejes X e Y.
    """
    x_min = min(min(x1), min(x2))
    x_max = max(max(x1), max(x2))
    y_min = min(min(y1), min(y2))
    y_max = max(max(y1), max(y2))
    
    return x_min, x_max, y_min, y_max

def run_step05_verification(json_file_path, txt_file_path):
    """
    Genera gráficos comparando:
    - Posiciones originales (TXT).
    - Posiciones visualmente calibradas, interpoladas y originales (JSON).
    """
    # 📌 Leer JSON con nuevas posiciones
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_x_calib, json_y_calib, json_filenames_calib = [], [], []
    json_x_interp, json_y_interp, json_filenames_interp = [], [], []
    json_x_original, json_y_original, json_filenames_original = [], [], []

    for step_name, step_info in json_data.items():
        for item in step_info.get("items", []):
            if "X" in item and "Y" in item:
                if item["Calibration_Status"] == "visually calibrated":
                    json_x_calib.append(item["X"])
                    json_y_calib.append(item["Y"])
                    json_filenames_calib.append(item.get("Filename", "Unknown"))
                elif item["Calibration_Status"] == "estimated":
                    json_x_interp.append(item["X"])
                    json_y_interp.append(item["Y"])
                    json_filenames_interp.append(item.get("Filename", "Unknown"))
                elif item["Calibration_Status"] == "original":
                    json_x_original.append(item["X"])
                    json_y_original.append(item["Y"])
                    json_filenames_original.append(item.get("Filename", "Unknown"))

    # 📌 Leer TXT original
    txt_x, txt_y, txt_filenames = [], [], []
    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:  # Saltamos la cabecera
        parts = line.strip().split()
        if len(parts) >= 3:
            txt_x.append(float(parts[1]))  # X
            txt_y.append(float(parts[2]))  # Y
            txt_filenames.append(parts[0])  # Nombre de la imagen

    # 📌 Obtener límites comunes para ambos gráficos
    x_min, x_max, y_min, y_max = get_common_axis_limits(
        json_x_calib + json_x_interp + json_x_original, 
        json_y_calib + json_y_interp + json_y_original, 
        txt_x, txt_y
    )

    # 📌 Crear gráfico TXT original
    fig_txt = go.Figure()
    fig_txt.add_trace(go.Scatter(
        x=txt_x, y=txt_y, 
        mode="markers", 
        marker=dict(color="green", size=6), 
        name="TXT Original",
        text=txt_filenames,  # Muestra el nombre al hacer hover
        hoverinfo="text+x+y"
    ))
    fig_txt.update_layout(
        title="Posiciones Originales (TXT)",
        xaxis=dict(title="X", range=[x_min, x_max]), 
        yaxis=dict(title="Y", range=[y_min, y_max]),
        width=600, height=500
    )

    # 📌 Crear gráfico JSON con nuevas posiciones
    fig_json = go.Figure()

    fig_json.add_trace(go.Scatter(
        x=json_x_calib, y=json_y_calib, 
        mode="markers", 
        marker=dict(color="blue", size=6), 
        name="Visually Calibrated",
        text=json_filenames_calib,  
        hoverinfo="text+x+y"
    ))

    fig_json.add_trace(go.Scatter(
        x=json_x_interp, y=json_y_interp, 
        mode="markers", 
        marker=dict(color="red", size=6), 
        name="Interpolated",
        text=json_filenames_interp,  
        hoverinfo="text+x+y"
    ))

    fig_json.add_trace(go.Scatter(
        x=json_x_original, y=json_y_original, 
        mode="markers", 
        marker=dict(color="orange", size=6), 
        name="Original",
        text=json_filenames_original,  
        hoverinfo="text+x+y"
    ))

    fig_json.update_layout(
        title="Posiciones Visualmente Calibradas, Interpoladas y Originales",
        xaxis=dict(title="X", range=[x_min, x_max]), 
        yaxis=dict(title="Y", range=[y_min, y_max]),
        width=600, height=500
    )

    return fig_txt, fig_json
