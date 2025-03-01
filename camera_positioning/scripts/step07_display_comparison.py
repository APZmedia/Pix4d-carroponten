import plotly.graph_objects as go
import json
import math

def get_common_axis_limits(x1, y1, x2, y2):
    """
    Obtiene los límites comunes para los ejes X e Y.
    """
    x_min = min(min(x1), min(x2))
    x_max = max(max(x1), max(x2))
    y_min = min(min(y1), min(y2))
    y_max = max(max(y1), max(y2))
    
    return x_min, x_max, y_min, y_max

def extract_positions_and_orientations(json_file_path, txt_file_path):
    """
    Extrae posiciones y orientaciones de los archivos JSON y TXT.
    """
    # 📌 Leer JSON
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    json_x, json_y, json_u, json_v = [], [], [], []

    for step_name, step_info in json_data.items():
        for item in step_info.get("items", []):
            if "X" in item and "Y" in item and "Kappa" in item and item["X"] is not None and item["Y"] is not None:
                json_x.append(item["X"])
                json_y.append(item["Y"])
                angle = math.radians(item["Kappa"])  # Convertir Kappa a radianes
                
                scale_factor = 5  # Aumentar la visibilidad de los vectores
                json_u.append(math.cos(angle) * scale_factor)  # Componente X de la orientación
                json_v.append(math.sin(angle) * scale_factor)  # Componente Y de la orientación

    # 📌 Leer TXT
    txt_x, txt_y, txt_u, txt_v = [], [], [], []

    with open(txt_file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines[1:]:  # Saltamos la cabecera
        parts = line.strip().split()
        if len(parts) >= 4:
            x = float(parts[1])
            y = float(parts[2])
            kappa = float(parts[3])  # Asumimos que el TXT tiene Kappa en la columna 4
            txt_x.append(x)
            txt_y.append(y)
            
            angle = math.radians(kappa)
            txt_u.append(math.cos(angle) * scale_factor)
            txt_v.append(math.sin(angle) * scale_factor)

    return json_x, json_y, json_u, json_v, txt_x, txt_y, txt_u, txt_v

def run_step07(json_file_path, txt_file_path):
    """
    Genera dos gráficos comparativos (JSON vs TXT) asegurando que tengan
    la misma escala en los ejes X e Y e incluyendo la orientación.
    """
    # Extraer datos
    json_x, json_y, json_u, json_v, txt_x, txt_y, txt_u, txt_v = extract_positions_and_orientations(json_file_path, txt_file_path)

    # 📌 Obtener límites comunes para ambos gráficos
    x_min, x_max, y_min, y_max = get_common_axis_limits(json_x, json_y, txt_x, txt_y)

    # 📌 Crear gráfico JSON con vectores de orientación
    fig_json = go.Figure()
    fig_json.add_trace(go.Scatter(x=json_x, y=json_y, mode="markers", marker=dict(color="red"), name="JSON"))
    fig_json.add_trace(go.Cone(x=json_x, y=json_y, u=json_u, v=json_v, sizemode="absolute", sizeref=1, colorscale="reds", name="Orientación JSON"))
    
    fig_json.update_layout(title="Visualización de posiciones y orientación - JSON",
                           xaxis=dict(title="X", range=[x_min, x_max]), 
                           yaxis=dict(title="Y", range=[y_min, y_max]),
                           width=700, height=600)

    # 📌 Crear gráfico TXT con vectores de orientación
    fig_txt = go.Figure()
    fig_txt.add_trace(go.Scatter(x=txt_x, y=txt_y, mode="markers", marker=dict(color="green"), name="TXT"))
    fig_txt.add_trace(go.Cone(x=txt_x, y=txt_y, u=txt_u, v=txt_v, sizemode="absolute", sizeref=1, colorscale="greens", name="Orientación TXT"))
    
    fig_txt.update_layout(title="Visualización de posiciones y orientación - TXT",
                          xaxis=dict(title="X", range=[x_min, x_max]), 
                          yaxis=dict(title="Y", range=[y_min, y_max]),
                          width=700, height=600)

    return fig_json, fig_txt
