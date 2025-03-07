import os
import json
import shutil
import gradio as gr

def process_images(json_path, source_folder, dest_folder):
    # Load JSON data
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    # Iterate through sequences
    copied_files = []
    for sequence, details in data.items():
        sequence_folder = os.path.join(dest_folder, sequence)
        os.makedirs(sequence_folder, exist_ok=True)
        
        # Iterate through items in the sequence
        for item in details.get("items", []):
            if item.get("Calibration_Status") in ["original", "estimated", "visually calibrated"]:
                filename = item.get("Filename")
                source_path = os.path.join(source_folder, filename)
                dest_path = os.path.join(sequence_folder, filename)
                
                if os.path.exists(source_path):
                    shutil.copy2(source_path, dest_path)
                    copied_files.append(filename)
                else:
                    copied_files.append(f"[MISSING] {filename}")
    
    return f"Processed {len(copied_files)} files. Check destination folder. Missing files are marked."

# Gradio interface
def gradio_interface(json_file, source_folder, dest_folder):
    return process_images(json_file, source_folder, dest_folder)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Path to JSON file"),
        gr.Textbox(label="Source folder (where images are located)"),
        gr.Textbox(label="Destination folder")
    ],
    outputs="text",
    title="Image Sorter by Sequence",
    description="Copies images with known calibration into sequence-named subfolders."
)

if __name__ == "__main__":
    iface.launch()
