import gradio as gr
import os

# Importamos las funciones de cada step
from scripts.step01_update_json import run_step01
from scripts.step02_visualize import run_step02
#from scripts.step03_estimate_center import run_step03
#from scripts.step04_visual_calib import run_step04
#from scripts.step05_interpolation import run_step05
#from scripts.step06_orientation_propagation import run_step06
#from scripts.step07_display_comparison import run_step07
#from scripts.step08_export_csv import run_step08

def step01_handler(txt_file, input_json_path, output_json_path):
    """
    Función de callback para Step01 (Update JSON with .txt).
    """
    if txt_file is None:
        return "❌ Error: No se cargó ningún archivo .txt."
    if not input_json_path.strip():
        return "❌ Error: Falta ruta JSON de entrada."
    if not output_json_path.strip():
        return "❌ Error: Falta ruta JSON de salida."

    # Guardamos el archivo txt en /uploads
    os.makedirs("uploads", exist_ok=True)
    txt_file_path = os.path.join("uploads", txt_file.name)
    with open(txt_file_path, "wb") as f:
        f.write(txt_file.read())
    
    # Llamamos la función principal del step
    try:
        result_msg = run_step01(txt_file_path, input_json_path, output_json_path)
        return "✅ " + result_msg
    except Exception as e:
        return f"❌ Ocurrió un error: {e}"


def step02_handler(json_file_path, txt_file_path):
    """
    Función de callback para Step02 (Visualización).
    Debe retornar la figura Plotly (o un error).
    """
    import plotly
    import plotly.graph_objects as go

    if not json_file_path.strip():
        return None, "❌ Error: Falta JSON path."
    if not txt_file_path.strip():
        return None, "❌ Error: Falta TXT path."
    
    try:
        fig = run_step02(json_file_path, txt_file_path)
        # Para Gradio, devolvemos la figura Plotly y un mensaje
        return fig, "✅ Gráfico generado correctamente."
    except Exception as e:
        return None, f"❌ Error generando visualización: {e}"

def launch_ui():
    with gr.Blocks(title="Pipeline Carroponte") as demo:
        gr.Markdown("# Herramienta Principal - Carroponte")
        
        with gr.Tabs():
            # Step 01
            with gr.Tab("Step 01: Update JSON"):
                gr.Markdown("### 1) Cargar un archivo .txt y actualizar el JSON con coordenadas calibradas")
                txt_file_input = gr.File(label="Archivo .txt", file_types=[".txt"])
                json_in_text   = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences.json")
                json_out_text  = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_updated.json")
                run_btn_step01 = gr.Button("Actualizar JSON")
                status_step01  = gr.Textbox(label="Resultado", interactive=False)
                
                run_btn_step01.click(
                    fn=step01_handler,
                    inputs=[txt_file_input, json_in_text, json_out_text],
                    outputs=[status_step01]
                )
            
            # Step 02
            with gr.Tab("Step 02: Visualizar JSON & TXT"):
                gr.Markdown("### 2) Visualizar JSON y TXT lado a lado")
                json_path_box = gr.Textbox(label="Ruta JSON", value="data/ground_truth/all_sequences_updated.json")
                txt_path_box  = gr.Textbox(label="Ruta TXT", value="uploads/calib_data.txt")
                run_btn_step02 = gr.Button("Visualizar")
                
                plot_output = gr.Plot(label="Gráfico Comparativo")
                status_step02 = gr.Textbox(label="Resultado", interactive=False)
                
                run_btn_step02.click(
                    fn=step02_handler,
                    inputs=[json_path_box, txt_path_box],
                    outputs=[plot_output, status_step02]
                )
            
            # Step 03
            with gr.Tab("Step 03: Estimar Centro y Radio"):
                gr.Markdown("### 3) Aquí iría la lógica para estimar el centro & radio (circle_estimator)")
                # Inputs y botón para step03
                # run_btn_step03 = ...
                # status_step03  = ...
                # O un placeholder
                gr.Markdown("_(Placeholder)_")

            # Step 04
            with gr.Tab("Step 04: Calibración Visual"):
                gr.Markdown("### 4) Calibrar imágenes no calibradas usando ‘visual match IDs to columns.csv’")
                gr.Markdown("_(Placeholder)_")
            
            # Step 05
            with gr.Tab("Step 05: Interpolación"):
                gr.Markdown("### 5) Interpolación homogénea entre imágenes calibradas")
                gr.Markdown("_(Placeholder)_")
            
            # Step 06
            with gr.Tab("Step 06: Orientación"):
                gr.Markdown("### 6) Propagar orientación con OrientationCorrector")
                gr.Markdown("_(Placeholder)_")
            
            # Step 07
            with gr.Tab("Step 07: Comparación final"):
                gr.Markdown("### 7) Mostrar posiciones/orientaciones: original vs ‘visually calibrated’ vs ‘estimated’")
                gr.Markdown("_(Placeholder)_")
            
            # Step 08
            with gr.Tab("Step 08: Exportar CSV"):
                gr.Markdown("### 8) Exportar CSV con posición y orientación en formato 4D")
                gr.Markdown("_(Placeholder)_")
    
    return demo


if __name__ == "__main__":
    app = launch_ui()
    app.launch()
