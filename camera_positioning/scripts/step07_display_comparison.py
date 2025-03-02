import plotly.graph_objects as go
import json
import math
import gradio as gr

def extract_positions_and_orientations(json_file_path, selected_sequences=None):
    """
    Extrae posiciones y orientaciones de las cámaras desde el archivo JSON.
    Filtra por secuencia si se proporciona una.
    """
    with open(json_file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    x_positions, y_positions, u_vectors, v_vectors, categories = [], [], [], [], []
    category_colors = {"original": "red", "visually calibrated": "green", "estimated": "blue"}

    for step_name, step_info in json_data.items():
        if selected_sequences and step_name not in selected_sequences:
            continue
        
        for item in step_info.get("items", []):
            if all(k in item for k in ["X", "Y", "Kappa", "Category"]):
                x_positions.append(item["X"])
                y_positions.append(item["Y"])
                angle = math.radians(item["Kappa"])  # Convertir Kappa a radianes
                scale_factor = 10  # Aumentamos la escala para mejorar la visibilidad
                u_vectors.append(math.cos(angle) * scale_factor)
                v_vectors.append(math.sin(angle) * scale_factor)
                categories.append(category_colors.get(item["Category"], "gray"))
    
    return x_positions, y_positions, u_vectors, v_vectors, categories

def visualize_camera_positions(json_file_path, selected_sequences):
    """
    Genera un gráfico con las posiciones y orientaciones de las cámaras.
    """
    x_positions, y_positions, u_vectors, v_vectors, categories = extract_positions_and_orientations(json_file_path, selected_sequences)

    fig = go.Figure()
    
    # Agregar puntos de diferentes categorías con diferentes colores
    for category, color in {"original": "red", "visually calibrated": "green", "estimated": "blue"}.items():
        indices = [i for i, cat in enumerate(categories) if cat == color]
        fig.add_trace(go.Scatter(
            x=[x_positions[i] for i in indices],
            y=[y_positions[i] for i in indices],
            mode="markers",
            marker=dict(color=color, size=4),
            name=category
        ))
    
    # Dibujar vectores de orientación como líneas con código de color
    for x, y, u, v, color in zip(x_positions, y_positions, u_vectors, v_vectors, categories):
        fig.add_trace(go.Scatter(x=[x, x + u], y=[y, y + v], mode='lines', line=dict(color=color, width=2), name="Orientación"))
    
    fig.update_layout(title="Visualización de posiciones y orientación de cámaras",
                      xaxis=dict(title="X"),
                      yaxis=dict(title="Y"),
                      width=800, height=700)
    
    return fig