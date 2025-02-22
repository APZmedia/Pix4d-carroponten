import gradio as gr
import os
from pathlib import Path
from update_all_sequences import update_all_sequences

def process_file(file):
    """Handles the uploaded file and updates all_sequences.json"""
    if file is None:
        return "No file uploaded. Please upload a calibration file."
    
    file_path = Path("uploads") / file.name
    file_path.parent.mkdir(parents=True, exist_ok=True)  # Ensure the uploads directory exists
    
    with open(file_path, "wb") as f:
        f.write(file.read())
    
    update_all_sequences(file_path)
    return f"Calibration data applied successfully from {file_path.name}!"

with gr.Blocks() as demo:
    gr.Markdown("# Camera Calibration Update")
    gr.Markdown("Upload a calibration file to update camera parameters in all_sequences.json")
    
    with gr.Row():
        file_input = gr.File(label="Upload Calibration File (.txt)", file_types=[".txt"])
        submit_btn = gr.Button("Update Calibration Data")
    
    output_message = gr.Textbox(label="Status", interactive=False)
    
    submit_btn.click(fn=process_file, inputs=[file_input], outputs=[output_message])
    
if __name__ == "__main__":
    demo.launch()
