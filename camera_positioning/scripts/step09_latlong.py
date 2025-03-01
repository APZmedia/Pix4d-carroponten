import json
import csv
import math
import gradio as gr

def xy_to_latlon(x, y, center_lat, center_lon, scale_factor=0.00001):
    """
    Convierte coordenadas locales X, Y a latitud y longitud aproximadas.
    Utiliza un factor de escala para convertir metros a grados.
    """
    lat = center_lat + (y * scale_factor)  # Ajuste de Norte-Sur
    lon = center_lon + (x * scale_factor)  # Ajuste de Este-Oeste
    return lat, lon

def add_latlon_to_json(json_input_path, json_output_path, center_lat, center_lon):
    """
    Agrega latitud y longitud a cada imagen en el JSON usando un centro geográfico.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)

    for step_name, step_info in sequences_data.items():
        for item in step_info.get("items", []):
            if "X" in item and "Y" in item:
                lat, lon = xy_to_latlon(item["X"], item["Y"], center_lat, center_lon)
                item["Latitude"] = lat
                item["Longitude"] = lon
    
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(sequences_data, f, indent=4)
    
    print(f"✅ Latitudes y longitudes agregadas. Guardado en {json_output_path}")

def export_csv_with_latlon(json_input_path, csv_output_path):
    """
    Exporta un CSV con las columnas estándar más latitud y longitud.
    """
    with open(json_input_path, "r", encoding="utf-8") as f:
        sequences_data = json.load(f)
    
    with open(csv_output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["#Image", "X", "Y", "Z", "Omega", "Phi", "Kappa", "SigmaHoriz", "SigmaVert", "Latitude", "Longitude"])
        
        for step_name, step_info in sequences_data.items():
            for item in step_info.get("items", []):
                writer.writerow([
                    item.get("Filename", "Unknown"),
                    item.get("X", 0.0),
                    item.get("Y", 0.0),
                    item.get("Z", 0.0),
                    item.get("Omega", 0.0),
                    item.get("Phi", 0.0),
                    item.get("Kappa", 0.0),
                    1.0,  # SigmaHoriz ajustado
                    0.3,  # SigmaVert ajustado
                    item.get("Latitude", 0.0),
                    item.get("Longitude", 0.0)
                ])
    
    print(f"✅ CSV con coordenadas geográficas exportado en {csv_output_path}")

def run_step09(json_input_path, json_output_path, csv_output_path, center_lat, center_lon):
    """
    Ejecuta Step09: agrega lat/lon al JSON y exporta CSV con coordenadas geográficas.
    """
    add_latlon_to_json(json_input_path, json_output_path, center_lat, center_lon)
    export_csv_with_latlon(json_output_path, csv_output_path)
    return f"✅ Step09 completado. JSON en {json_output_path}, CSV en {csv_output_path}"

def launch_ui():
    with gr.Blocks(title="Pipeline Carroponte") as demo:
        gr.Markdown("# Step 09: Agregar Latitud y Longitud")
        json_input_path = gr.Textbox(label="Ruta JSON de entrada", value="data/ground_truth/all_sequences_oriented.json")
        json_output_path = gr.Textbox(label="Ruta JSON de salida", value="data/ground_truth/all_sequences_with_latlon.json")
        csv_output_path = gr.Textbox(label="Ruta CSV de salida", value="data/ground_truth/pix4d_export_with_latlon.csv")
        center_lat = gr.Number(label="Latitud del centro", value=0.0)
        center_lon = gr.Number(label="Longitud del centro", value=0.0)
        run_btn_step09 = gr.Button("Generar JSON y CSV con coordenadas")
        status_step09 = gr.Textbox(label="Resultado", interactive=False)

        run_btn_step09.click(
            fn=run_step09,
            inputs=[json_input_path, json_output_path, csv_output_path, center_lat, center_lon],
            outputs=[status_step09]
        )
    
    return demo

if __name__ == "__main__":
    app = launch_ui()
    app.launch()
