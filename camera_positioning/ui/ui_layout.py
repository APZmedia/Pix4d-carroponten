from data.sequence_handler import get_image_info
import gradio as gr

def create_ui():
    """Creates the Gradio UI layout."""

    with gr.Blocks() as demo:
        gr.Markdown("# Camera Position Editor")

        with gr.Row():
            corrected_id_input = gr.Number(label="Corrected ID", value=4014, interactive=True)
            load_btn = gr.Button("Load")
            show_toggle = gr.Checkbox(label="Show Ground Truth Data", value=True)
            
        ground_truth_info = gr.Textbox(label="Ground Truth Info", interactive=False)

        def load_ground_truth_info(corrected_id):
            """Fetches and displays ground truth data for a given image ID."""
            info = get_image_info(int(corrected_id))
            return f"Filename: {info.get('Filename', 'N/A')}\nTimestamp: {info.get('Timestamp', 'N/A')}\nSequence: {info.get('Sequence', 'N/A')}"

        load_btn.click(fn=load_ground_truth_info, inputs=[corrected_id_input], outputs=[ground_truth_info])

    return demo
