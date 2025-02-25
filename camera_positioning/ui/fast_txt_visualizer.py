import gradio as gr
import plotly.graph_objects as go
import pandas as pd

def parse_file(file_path):
    """Parses the input file and extracts X, Y coordinates."""
    data = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for line in lines[1:]:  # Omitir encabezado
            parts = line.strip().split()
            if len(parts) >= 3:
                image_name = parts[0]
                try:
                    x = float(parts[1])
                    y = float(parts[2])
                    data.append({"image": image_name, "X": x, "Y": y})
                except ValueError:
                    continue  # Ignorar líneas con datos no válidos
    
    return pd.DataFrame(data)

def plot_coordinates(file):
    """Reads the uploaded file and generates a scatter plot of X, Y coordinates."""
    if file is None:
        return go.Figure()

    df = parse_file(file.name)

    fig = go.Figure()

    # Agregar separaciones entre puntos de distintas secuencias usando distancia
    x_values = []
    y_values = []

    prev_x, prev_y = None, None
    for _, row in df.iterrows():
        if prev_x is not None and prev_y is not None:
            distance = ((row["X"] - prev_x) ** 2 + (row["Y"] - prev_y) ** 2) ** 0.5
            if distance > 5:  # Ajustar este umbral según la separación esperada entre imágenes
                x_values.append(None)  # Agregar break en la línea
                y_values.append(None)

        x_values.append(row["X"])
        y_values.append(row["Y"])
        prev_x, prev_y = row["X"], row["Y"]

    fig.add_trace(go.Scatter(
        x=x_values, y=y_values,
        mode="markers+lines",
        text=df["image"],
        marker=dict(color="blue", size=6),
        name="Posiciones X, Y"
    ))

    # Configurar escala homogénea
    fig.update_layout(
        title="Visualización de Coordenadas X, Y",
        xaxis_title="X",
        yaxis_title="Y",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
        height=600
    )

    return fig

# Crear la interfaz en Gradio
demo = gr.Interface(
    fn=plot_coordinates,
    inputs=gr.File(label="Arrastra y suelta tu archivo"),
    outputs=gr.Plot(label="Gráfico de Coordenadas"),
    title="Visualización de Coordenadas X, Y",
    description="Carga un archivo de parámetros calibrados y visualiza las posiciones X, Y en un gráfico interactivo."
)

# Iniciar la aplicación
demo.launch()
