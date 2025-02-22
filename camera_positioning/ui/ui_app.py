import gradio as gr
import os
import io
import csv
import plotly.graph_objects as go

# Importamos las funciones que creamos:
from data.json_handler import (
    load_sequences_json,
    save_sequences_json
)
from data.pix4d_import import (
    load_pix4d_calibrations,
    apply_calibrations_to_json
)
from data.pix4d_export import export_to_pix4d_csv
from processing.cluster_calibrator import calibrate_all_sequences
from config import CENTER

import numpy as np
import math

#########################
# Funciones de ayuda
#########################

def compute_sequence_radius(step_info, center):
    """
    Calcula el radio a partir de las imágenes calibradas en step_info (campo 'original').
    """
    distances = []
    for item in step_info["items"]:
        if item.get("Calibration_Status") == "original":
            x, y = item.get("X"), item.get("Y")
            if x is not None and y is not None:
                dx = x - center[0]
                dy = y - center[1]
                dist = math.sqrt(dx*dx + dy*dy)
                distances.append(dist)
    if len(distances) == 0:
        return None
    return float(np.median(distances))

def update_sequence_radii(all_data, center):
    """
    Para cada StepXX, si no tiene radio, lo calculamos por la mediana de distancias de las calibradas.
    """
    for step_name, step_info in all_data.items():
        radius = compute_sequence_radius(step_info, center)
        if radius is not None:
            step_info["calculated_radius"] = radius
    return all_data

def create_plot(all_data):
    """
    Crea una figura Plotly con:
    - Puntos rojos para 'original' (calibrados).
    - Puntos verdes para 'estimated'.
    - Puntos grises para 'uncalibrated'.
    - Un marker en el 'center'.
    """
    fig = go.Figure()

    # Listas para cada tipo
    x_orig, y_orig = [], []
    x_est, y_est = [], []
    x_unc, y_unc = [], []

    for step_name, step_info in all_data.items():
        for item in step_info["items"]:
            x = item.get("X", None)
            y = item.get("Y", None)
            if x is None or y is None:
                continue
            status = item.get("Calibration_Status", "uncalibrated")
            if status == "original":
                x_orig.append(x)
                y_orig.append(y)
            elif status == "estimated":
                x_est.append(x)
                y_est.append(y)
            else:
                x_unc.append(x)
                y_unc.append(y)

    # Puntos calibrados (rojo)
    if x_orig and y_orig:
        fig.add_trace(go.Scatter(
            x=x_orig, y=y_orig,
            mode='markers',
            marker=dict(color='red', symbol='circle', size=7),
            name='Calibradas (original)'
        ))
    # Puntos estimados (verde)
    if x_est and y_est:
        fig.add_trace(go.Scatter(
            x=x_est, y=y_est,
            mode='markers',
            marker=dict(color='green', symbol='circle-open', size=7),
            name='Estimadas'
        ))
    # Puntos uncalibrated (gris)
    if x_unc and y_unc:
        fig.add_trace(go.Scatter(
            x=x_unc, y=y_unc,
            mode='markers',
            marker=dict(color='gray', symbol='x', size=6),
            name='Sin calibrar'
        ))

    # Agregamos el centro en púrpura
    cx, cy = CENTER[0], CENTER[1]
    fig.add_trace(go.Scatter(
        x=[cx],
        y=[cy],
        mode='markers',
        marker=dict(color='purple', symbol='star', size=12),
        name='Center'
    ))

    fig.update_layout(
        title="Visualización de Cámaras Carroponte",
        xaxis_title="X",
        yaxis_title="Y",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )
    return fig

def pipeline(json_data, calib_csv):
    """
    Ejecuta el pipeline completo:
      1) Carga JSON desde memoria (json_data).
      2) Carga calibraciones (calib_csv).
      3) Aplica calibraciones.
      4) Calcula radio de cada secuencia.
      5) Calibra clusters (interpolación).
      6) Retorna all_data modificado.
    """
    # Gradio pasa el contenido del JSON como string, si usas 'File' para JSON.
    # Si usas un path, deberías adaptarlo. Aquí supondremos que json_data es un string con JSON.
    import json
    all_data = json.loads(json_data)

    # 2) Cargar calibraciones de Pix4D
    # Gradio 'calib_csv' es un NamedTemporaryFile, leemos su path:
    if calib_csv is not None:
        pix4d_path = calib_csv.name
        calibrations = load_pix4d_calibrations(pix4d_path)
        # 3) Aplica calibraciones
        all_data = apply_calibrations_to_json(all_data, calibrations)
    else:
        # Si no se sube CSV, no hace nada
        pass

    # 4) Calcular/actualizar radios
    all_data = update_sequence_radii(all_data, CENTER)

    # 5) Propagación / interpolación
    all_data = calibrate_all_sequences(all_data, CENTER)

    return all_data

def run_pipeline(json_file_obj, csv_file_obj):
    """
    Toma los archivos subidos en Gradio, ejecuta pipeline, retorna:
      - Plot final (Plotly)
      - CSV final (para descargar)
    """
    if not json_file_obj:
        return "ERROR: Debes subir un archivo JSON con las secuencias", None

    # Leemos el JSON subido
    with open(json_file_obj.name, "r", encoding="utf-8") as f:
        json_str = f.read()

    # 1..5) Corre pipeline
    all_data = pipeline(json_str, csv_file_obj)

    # 6) Generamos CSV Pix4D en memoria (usaremos io.StringIO)
    output_csv_buffer = io.StringIO()
    writer = csv.writer(output_csv_buffer, lineterminator="\n")
    writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert"])

    # Usamos lógica de export sin necesidad de un path:
    for step_name, step_info in all_data.items():
        for item in step_info["items"]:
            fname = item["Filename"]
            x = float(item.get("X", 0.0))
            y = float(item.get("Y", 0.0))
            z = float(item.get("Z", 0.0))
            Omega = float(item.get("Omega", 0.0))
            Phi = float(item.get("Phi", 0.0))
            Kappa = float(item.get("Kappa", 0.0))

            status = item.get("Calibration_Status", "uncalibrated")
            if status == "original":
                sigma_h, sigma_v = 0.5, 0.2
            elif status == "estimated":
                sigma_h, sigma_v = 2.0, 0.2
            else:
                sigma_h, sigma_v = 5.0, 1.0

            writer.writerow([fname, x, y, z, Omega, Phi, Kappa, sigma_h, sigma_v])

    # Convertimos a un "File-like" que Gradio pueda devolver
    final_csv_bytes = output_csv_buffer.getvalue().encode("utf-8")

    # 7) Creamos la gráfica
    fig = create_plot(all_data)

    return fig, final_csv_bytes

#########################
# Construcción de la UI
#########################

def launch_ui():
    with gr.Blocks(title="Carroponte Calibration Tool") as demo:
        gr.Markdown("## Carroponte Calibration & Visualization")

        with gr.Row():
            json_file = gr.File(label="Subir JSON (all_sequences_clustered.json)", file_types=['json'])
            csv_file = gr.File(label="(Opcional) Subir CSV Pix4D calibrations")

        run_btn = gr.Button("Ejecutar Pipeline")
        plot_output = gr.Plot(label="Vista Plotly")
        download_csv = gr.File(label="Descarga CSV Pix4D", interactive=False)

        # Definimos la callback
        def on_run_pipeline(jf, cf):
            result = run_pipeline(jf, cf)
            if isinstance(result, str):
                # error
                return gr.update(value=result), None
            else:
                fig, csv_data = result
                # devuelvo la figura y un archivo "virtual" con el CSV
                return fig, (csv_data, "resultado_pix4d.csv")

        # Conectamos el botón
        run_btn.click(fn=on_run_pipeline, inputs=[json_file, csv_file], outputs=[plot_output, download_csv])

    return demo

if __name__ == "__main__":
    demo = launch_ui()
    demo.launch()
