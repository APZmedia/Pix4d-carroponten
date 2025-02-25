import plotly.graph_objects as go
import json

def get_common_axis_limits(x1, y1, x2, y2):
    """
    Obtiene los límites comunes para los ejes X e Y.
    """
    x_min = min(min(x1), min(x2))
    x_max = max(max(x1), max(x2))
    y_min = min(min(y1), min(y2))
    y_max = max(max(y1), max(y2))
    
    return x_min, x_max, y_min, y_max

def run_step02(json_file_path, txt_file_path):
    """
    Genera dos gráficos comparativos (JSON vs TXT) asegurando que tengan
    la misma escala en los ejes X e Y.
    """
    # 📌 Leer JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_x, json_y = [], []

    for step_name, step_info in json_data.items():
        for item in step_info.get("items", []):
            if "X" in item and "Y" in item and item["X"] is not None and item["Y"] is not None:
                json_x.append(item["X"])
                json_y.append(item["Y"])

    # 📌 Leer TXT
    txt_x, txt_y = [], []

    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:  # Saltamos la cabecera
        parts = line.strip().split()
        if len(parts) >= 3:
            txt_x.append(float(parts[1]))  # X
            txt_y.append(float(parts[2]))  # Y

    # 📌 Obtener límites comunes para ambos gráficos
    x_min, x_max, y_min, y_max = get_common_axis_limits(json_x, json_y, txt_x, txt_y)

    # 📌 Crear gráfico JSON
    fig_json = go.Figure()
    fig_json.add_trace(go.Scatter(x=json_x, y=json_y, mode="markers", marker=dict(color="red"), name="JSON"))
    fig_json.update_layout(title="Visualización de posiciones - JSON",
                           xaxis=dict(title="X", range=[x_min, x_max]), 
                           yaxis=dict(title="Y", range=[y_min, y_max]),
                           width=600, height=500)

    # 📌 Crear gráfico TXT
    fig_txt = go.Figure()
    fig_txt.add_trace(go.Scatter(x=txt_x, y=txt_y, mode="markers", marker=dict(color="green"), name="TXT"))
    fig_txt.update_layout(title="Visualización de posiciones - TXT",
                          xaxis=dict(title="X", range=[x_min, x_max]), 
                          yaxis=dict(title="Y", range=[y_min, y_max]),
                          width=600, height=500)

    return fig_json, fig_txt
