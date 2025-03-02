import gradio as gr
import os

# Importamos las funciones de cada step
from scripts.step01_update_json import run_step01
from scripts.step02_visualize import run_step02
from scripts.step03_estimate_center import estimate_center_and_radius
from scripts.step04_visual_calib import calibrate_visually
from scripts.step05_interpolation import interpolate_positions
from scripts.step05_verification import run_step05_verification
from scripts.step06_orientation_propagation import propagate_orientation
from scripts.step07_display_comparison import visualize_camera_positions
from scripts.step08_export_csv import run_step08

def step01_handler(txt_file, input_json_path, output_json_path):
    """
    Maneja la ejecución del Step01 (Actualización de JSON con el TXT subido).
    """
    if txt_file is None:
        return "❌ Error: No se cargó ningún archivo .txt."
    
    if not input_json_path.strip():
        return "❌ Error: No se especificó el JSON de entrada."
    
    if not output_json_path.strip():
        return "❌ Error: No se especificó el JSON de salida."
    
    # Gradio proporciona un objeto con la ruta del archivo subido
    txt_file_path = txt_file.name

    # Llamamos a `run_step01`, pasándole la ruta directamente
    try:
        result_msg = run_step01(txt_file_path, input_json_path, output_json_path)
        return "✅ " + result_msg
    except Exception as e:
        return f"❌ Ocurrió un error actualizando el JSON: {e}"

def step02_handler(json_file_path, txt_file_path):
    """
    Función de callback para Step02 (Visualización).
    Genera dos gráficos comparativos: uno para el JSON y otro para el TXT.
    """
    if not json_file_path.strip():
        return None, None, "❌ Error: Falta JSON path."
    if not txt_file_path.strip():
        return None, None, "❌ Error: Falta TXT path."
    
    try:
        fig_json, fig_txt = run_step02(json_file_path, txt_file_path)  # ✅ Generamos dos gráficos
        return fig_json, fig_txt, "✅ Gráficos generados correctamente."
    except Exception as e:
        return None, None, f"❌ Error generando visualización: {e}"

def step03_handler(input_json_path, output_json_path):
    """
    Función de callback para Step03 (Cálculo del centro y radio por secuencia).
    """
    if not input_json_path.strip():
        return "❌ Error: Falta JSON path de entrada."
    
    if not output_json_path.strip():
        return "❌ Error: Falta JSON path de salida."
    
    try:
        estimate_center_and_radius(input_json_path, output_json_path)
        return f"✅ Centros y radios estimados guardados en {output_json_path}"
    except Exception as e:
        return f"❌ Error estimando el centro: {e}"

def step04_handler(input_json_path, csv_input_path, output_json_path):
    """
    Función de callback para Step04 (Calibración Visual).
    """
    if not input_json_path.strip():
        return "❌ Error: Falta JSON path de entrada."
    
    if not csv_input_path.strip():
        return "❌ Error: Falta CSV path de entrada."
    
    if not output_json_path.strip():
        return "❌ Error: Falta JSON path de salida."
    
    try:
        calibrate_visually(input_json_path, csv_input_path, output_json_path)
        return f"✅ Calibración visual guardada en {output_json_path}"
    except Exception as e:
        return f"❌ Error en la calibración visual: {e}"

def step05_handler(input_json_path, output_json_path):
    """
    Función de callback para Step05 (Interpolación de imágenes sin calibrar).
    """
    if not input_json_path.strip():
        return "❌ Error: Falta JSON path de entrada."
    
    if not output_json_path.strip():
        return "❌ Error: Falta JSON path de salida."
    
    try:
        interpolate_positions(input_json_path, output_json_path)
        return f"✅ Interpolación guardada en {output_json_path}"
    except Exception as e:
        return f"❌ Error en la interpolación: {e}"

def step05_verification_handler(json_file_path, txt_file_path):
    """
    Función de callback para Step05 Verificación.
    Genera gráficos comparativos de posiciones originales vs. nuevas posiciones.
    """
    if not json_file_path.strip():
        return None, None, "❌ Error: Falta JSON path."
    if not txt_file_path.strip():
        return None, None, "❌ Error: Falta TXT path."
    
    try:
        fig_txt, fig_json = run_step05_verification(json_file_path, txt_file_path)
        return fig_txt, fig_json, "✅ Gráficos generados correctamente."
    except Exception as e:
        return None, None, f"❌ Error generando visualización: {e}"

def step06_handler(json_input_path, json_output_path):
    """
    Maneja la ejecución del Step06 (Propagación de Orientación).
    """
    if not json_input_path.strip():
        return "❌ Error: No se especificó el JSON de entrada."
    
    if not json_output_path.strip():
        return "❌ Error: No se especificó el JSON de salida."

    try:
        propagate_orientation(json_input_path, json_output_path)
        return f"✅ Propagación de orientación completada. JSON guardado en {json_output_path}"
    except Exception as e:
        return f"❌ Error en la propagación de orientación: {e}"

def step07_handler(json_file_path, txt_file_path):
    """
    Función de callback para Step07 (Comparación final de posiciones y orientación).
    """
    if not json_file_path.strip():
        return None, "❌ Error: Falta JSON path."
    if not txt_file_path.strip():
        return None, "❌ Error: Falta TXT path."
    
    try:
        fig_json = visualize_camera_positions(json_file_path)
        return fig_json, "✅ Gráficos generados correctamente."
    except Exception as e:
        return None, f"❌ Error generando visualización: {e}"


def step08_handler(json_input_path, csv_output_path):
    """
    Maneja la ejecución del Step08 (Exportación a CSV).
    """
    if not json_input_path.strip():
        return "❌ Error: No se especificó el JSON de entrada."
    
    if not csv_output_path.strip():
        return "❌ Error: No se especificó la ruta de salida del CSV."

    try:
        result_msg = run_step08(json_input_path, csv_output_path)
        return result_msg
    except Exception as e:
        return f"❌ Error en la exportación a CSV: {e}"

def step09_handler(json_input_path, json_output_path, lat_center, lon_center):
    """
    Maneja la ejecución del Step09 (Asignar coordenadas geográficas y exportar CSV).
    """
    if not json_input_path.strip():
        return "❌ Error: No se especificó el JSON de entrada."
    
    if not json_output_path.strip():
        return "❌ Error: No se especificó la ruta de salida del JSON."
    
    try:
        result_msg = run_step09(json_input_path, json_output_path, lat_center, lon_center)
        return result_msg
    except Exception as e:
        return f"❌ Error en la asignación de coordenadas: {e}"

def launch_ui():
    with gr.Blocks(title="Pipeline Carroponte") as demo:
        gr.Markdown("# Herramienta Principal - Carroponte")
        
        with gr.Tabs():
            # Step 01
            with gr.Tab("Step 01: Update JSON"):
                gr.Markdown("### 1) Cargar un archivo .txt y actualizar el JSON con coordenadas calibradas")
                txt_file_input = gr.File(label="Archivo .txt", file_types=[".txt"])
                json_in_text   = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_clustered_updated.json")
                json_out_text  = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_updated.json")
                run_btn_step01 = gr.Button("Actualizar JSON")
                status_step01  = gr.Textbox(label="Resultado", interactive=False)
                
                run_btn_step01.click(
                    fn=step01_handler,
                    inputs=[txt_file_input, json_in_text, json_out_text],
                    outputs=[status_step01]
                )
            
            # Step 02 (✅ AHORA LOS GRÁFICOS ESTÁN UNO AL LADO DEL OTRO)
            with gr.Tab("Step 02: Visualizar JSON & TXT"):
                gr.Markdown("### 2) Comparación de posiciones en JSON y TXT")
                
                json_path_box = gr.Textbox(label="Ruta JSON", value="data/ground_truth/all_sequences_updated.json")
                txt_path_box  = gr.Textbox(label="Ruta TXT", value="input/XPR-finalmerge05 rebuild_calibrated_external_camera_parameters.txt")
                
                run_btn_step02 = gr.Button("Visualizar")

                # 📌 Layout de dos columnas para mostrar los gráficos lado a lado
                with gr.Row():
                    plot_output_json = gr.Plot(label="Visualización JSON")
                    plot_output_txt  = gr.Plot(label="Visualización TXT")
                
                status_step02 = gr.Textbox(label="Resultado", interactive=False)

                # Conectar botón con la función de visualización
                run_btn_step02.click(
                    fn=step02_handler,
                    inputs=[json_path_box, txt_path_box],
                    outputs=[plot_output_json, plot_output_txt, status_step02]
                )

            # Step 03
            with gr.Tab("Step 03: Estimar Centro y Radio"):
                gr.Markdown("### 3) Calcular el centro y el radio de cada secuencia a partir de imágenes calibradas.")
                
                json_in_text_step03   = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_updated.json")
                json_out_text_step03  = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_with_center.json")
                
                run_btn_step03 = gr.Button("Calcular Centro y Radio")
                status_step03  = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step03.click(
                    fn=step03_handler,
                    inputs=[json_in_text_step03, json_out_text_step03],
                    outputs=[status_step03]
                )

            # Step 04
            with gr.Tab("Step 04: Calibración Visual"):
                gr.Markdown("### 4) Calibrar imágenes no calibradas usando ‘visual match IDs to columns.csv’")

                json_in_text_step04   = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_with_center.json")
                csv_in_text_step04    = gr.Textbox(label="Ruta CSV con ángulos", value="data/ground_truth/Visual match IDs to columns.csv")
                json_out_text_step04  = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_visually_calibrated.json")

                run_btn_step04 = gr.Button("Calibrar Visualmente")
                status_step04  = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step04.click(
                    fn=step04_handler,
                    inputs=[json_in_text_step04, csv_in_text_step04, json_out_text_step04],
                    outputs=[status_step04]
                )

            # Step 05
            with gr.Tab("Step 05: Interpolación"):
                gr.Markdown("### 5) Interpolar imágenes sin calibrar siguiendo la trayectoria circular.")

                json_in_text_step05   = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_visually_calibrated.json")
                json_out_text_step05  = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_interpolated.json")

                run_btn_step05 = gr.Button("Interpolar")
                status_step05  = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step05.click(
                    fn=step05_handler,
                    inputs=[json_in_text_step05, json_out_text_step05],
                    outputs=[status_step05]
                )
            # Step 05 Verificación
            with gr.Tab("Step 05 Verificación"):
                gr.Markdown("### 5) Comparación de posiciones originales (TXT) vs. nuevas posiciones (JSON).")

                json_path_box = gr.Textbox(label="Ruta JSON", value="data/ground_truth/all_sequences_interpolated.json")
                txt_path_box  = gr.Textbox(label="Ruta TXT", value="input/XPR-finalmerge05 rebuild_calibrated_external_camera_parameters.txt")

                run_btn_step05_verification = gr.Button("Generar Comparación")

                # 📌 Layout con dos gráficos lado a lado
                with gr.Row():
                    plot_output_txt  = gr.Plot(label="TXT Original")
                    plot_output_json = gr.Plot(label="Posiciones Estimadas")

                status_step05_verification = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step05_verification.click(
                    fn=step05_verification_handler,
                    inputs=[json_path_box, txt_path_box],
                    outputs=[plot_output_txt, plot_output_json, status_step05_verification]
                )

            # Step 06
            with gr.Tab("Step 06: Propagar Orientación"):
                gr.Markdown("### 6) Propagar orientación con el patrón de rotación identificado en cada secuencia")
                
                json_input_path = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_interpolated.json")
                json_output_path = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_oriented.json")

                run_btn_step06 = gr.Button("Propagar Orientación")
                status_step06 = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step06.click(
                    fn=step06_handler,
                    inputs=[json_input_path, json_output_path],
                    outputs=[status_step06]
                )
            
            #Step 07
            with gr.Tab("Step 07: Comparación final"):
                gr.Markdown("### 7) Mostrar posiciones/orientaciones: original vs ‘visually calibrated’ vs ‘estimated’")
                json_path_box = gr.Textbox(label="Ruta JSON", value="data/ground_truth/all_sequences_oriented.json")
                sequence_filter = gr.CheckboxGroup(choices=[], label="Filtrar por Secuencias")
                run_btn_step07 = gr.Button("Generar Comparación")
                
                with gr.Row():
                    plot_output_json = gr.Plot(label="Visualización JSON")
                
                status_step07 = gr.Textbox(label="Resultado", interactive=False)
                
                run_btn_step07.click(
                    fn=step07_handler,
                    inputs=[json_path_box, sequence_filter],
                    outputs=[plot_output_json, status_step07]
                )

            
            # Step 08
            with gr.Tab("Step 08: Exportar CSV"):
                gr.Markdown("### 8) Exportar CSV con posición y orientación en formato Pix4D")

                json_input_path = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_oriented.json")
                csv_output_path = gr.Textbox(label="Ruta CSV de salida", value="data/ground_truth/pix4d_export.csv")

                run_btn_step08 = gr.Button("Exportar a CSV")
                status_step08 = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step08.click(
                    fn=step08_handler,
                    inputs=[json_input_path, csv_output_path],
                    outputs=[status_step08]
                )
            # Step 09
            with gr.Tab("Step 09: Asignar Coordenadas Geográficas"):
                gr.Markdown("### 9) Asignar latitud y longitud al centro de la posición de todas las imágenes")
                json_input_path = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_oriented.json")
                json_output_path = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_georeferenced.json")
                lat_center = gr.Number(label="Latitud del Centro", value=0.0)
                lon_center = gr.Number(label="Longitud del Centro", value=0.0)
                
                run_btn_step09 = gr.Button("Asignar Coordenadas")
                status_step09 = gr.Textbox(label="Resultado", interactive=False)

                run_btn_step09.click(
                    fn=step09_handler,
                    inputs=[json_input_path, json_output_path, lat_center, lon_center],
                    outputs=[status_step09]
                )
    
    return demo


if __name__ == "__main__":
    app = launch_ui()
    app.launch()
