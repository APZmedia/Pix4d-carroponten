import gradio as gr
import os
import io
import csv
import tempfile
import plotly.graph_objects as go

# Módulos que ya tienes en tu repo
from data.json_handler import (
    load_sequences_json,
    save_sequences_json
)
from processing.cluster_calibrator import calibrate_all_sequences
from config import CENTER

import numpy as np
import math
import json

#########################
# Funciones de ayuda
#########################

def parse_initial_txt(txt_path):
    """
    Ejemplo de parseo del TXT inicial.
    Ajusta esta función para extraer la info que necesites.
    """
    with open(txt_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    return {
        "num_lines": len(lines),
        "lines": lines
    }

def compute_sequence_radius(step_info, center):
    """
    Calcula el radio a partir de las imágenes 'original' (calibradas).
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
    return float(np.median(distances)) if distances else None

def update_sequence_radii(all_data, center):
    """
    Para cada StepXX, si no tiene radio definido, lo calculamos por la mediana de distancias.
    """
    for step_name, step_info in all_data.items():
        radius = compute_sequence_radius(step_info, center)
        if radius is not None:
            step_info["calculated_radius"] = radius
    return all_data

def create_plot(all_data):
    """
    Crea un Plotly Figure con:
      - Puntos rojos (original/calibradas)
      - Puntos verdes (estimated)
      - Puntos grises (uncalibrated)
      - El 'center' en púrpura
    """
    fig = go.Figure()

    x_orig, y_orig = [], []
    x_est, y_est = [], []
    x_unc, y_unc = [], []

    for step_name, step_info in all_data.items():
        for item in step_info["items"]:
            x = item.get("X")
            y = item.get("Y")
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

    if x_orig and y_orig:
        fig.add_trace(go.Scatter(x=x_orig, y=y_orig, mode='markers',
                                 marker=dict(color='red', size=6),
                                 name='Calibradas (original)'))

    if x_est and y_est:
        fig.add_trace(go.Scatter(x=x_est, y=y_est, mode='markers',
                                 marker=dict(color='green', size=6),
                                 name='Estimadas'))

    if x_unc and y_unc:
        fig.add_trace(go.Scatter(x=x_unc, y=y_unc, mode='markers',
                                 marker=dict(color='gray', size=6, symbol='x'),
                                 name='Sin calibrar'))

    fig.add_trace(go.Scatter(x=[CENTER[0]], y=[CENTER[1]], mode='markers',
                             marker=dict(color='purple', symbol='star', size=12),
                             name='Center'))

    fig.update_layout(
        title="Visualización Cámaras (Carroponte)",
        xaxis_title="X",
        yaxis_title="Y",
        xaxis=dict(scaleanchor="y", scaleratio=1),
        yaxis=dict(scaleanchor="x", scaleratio=1),
    )
    return fig

#########################
# Pipeline principal
#########################

def pipeline(txt_file_path=None):
    """
    Ejecuta la lógica:
      1) Cargar JSON desde data/ground_truth/all_sequences.json
      2) (Opcional) procesar el TXT inicial
      3) Calcular radios
      4) Calibrar clusters (propagar estimaciones)
      5) Devuelve all_data final
    """

    all_data = load_sequences_json()

    if txt_file_path is not None:
        info_txt = parse_initial_txt(txt_file_path)
        print(f"TXT subido. Contiene {info_txt['num_lines']} líneas.")

    all_data = update_sequence_radii(all_data, CENTER)
    all_data = calibrate_all_sequences(all_data, CENTER)

    return all_data

def generate_pix4d_csv(all_data):
    """
    Genera un CSV con formato Pix4D y lo escribe en un archivo temporal.
    Retorna la ruta del archivo CSV para Gradio.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv", mode="w", encoding="utf-8", newline="") as temp_file:
        writer = csv.writer(temp_file)
        writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert"])

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
                sigma_h, sigma_v = (0.5, 0.2) if status == "original" else (2.0, 0.2) if status == "estimated" else (5.0, 1.0)

                writer.writerow([fname, x, y, z, Omega, Phi, Kappa, sigma_h, sigma_v])

        return temp_file.name  # Retornamos la ruta del archivo CSV

#########################
# Integración con Gradio
#########################

def run_pipeline(txt_file_obj):
    """
    Función llamada por Gradio al pulsar "Ejecutar Pipeline".
    Retorna:
      - La figura Plotly
      - Un archivo CSV final (para descargar)
    """
    if txt_file_obj is not None:
        all_data = pipeline(txt_file_obj.name)
    else:
        all_data = pipeline()

    fig = create_plot(all_data)

    csv_file_path = generate_pix4d_csv(all_data)

    return fig, csv_file_path  # Retornamos el path del CSV generado

def launch_ui():
    with gr.Blocks(title="Carroponte Calibration Tool") as demo:
        gr.Markdown("# Carroponte Calibration & Visualization")

        txt_file = gr.File(label="(Opcional) Arrastra tu TXT inicial", file_types=['text'])

        run_btn = gr.Button("Ejecutar Pipeline")

        plot_output = gr.Plot(label="Visualización Plotly")
        download_csv = gr.File(label="Descarga CSV Final", interactive=True)

        def on_run_pipeline(txt_f):
            return run_pipeline(txt_f)

        run_btn.click(fn=on_run_pipeline, inputs=[txt_file], outputs=[plot_output, download_csv])

    return demo

if __name__ == "__main__":
    demo_app = launch_ui()
    demo_app.launch()
