import gradio as gr
import requests
import json
import os

# Get API URL from environment variable, default to localhost if not set
API_URL = os.getenv("API_URL", "http://localhost:8000")

def get_diagram_types():
    response = requests.get(f"{API_URL}/diagram-types")
    return response.json()

def generate_and_render_diagram(prompt, diagram_type):
    try:
        response = requests.post(
            f"{API_URL}/generate-diagram",
            json={"prompt": prompt, "diagram_type": diagram_type}
        )
        
        if response.status_code != 200:
            return str(response.json()["detail"]), None, ""
        
        result = response.json()
        return result["mermaid_code"], result["image_path"], result["preview"]
    except Exception as e:
        return str(e), None, ""

def create_app():
    with gr.Blocks(title="Visual Aid Designer", theme=gr.themes.Soft()) as app:
        gr.Markdown("# 🎨 Visual Aid Designer\n\nGenerate beautiful diagrams from text descriptions!")
        
        with gr.Row():
            with gr.Column(scale=2):
                prompt_input = gr.Textbox(
                    label="Diagram Description",
                    placeholder="Describe the diagram you want to create...",
                    lines=5
                )
                diagram_type = gr.Dropdown(
                    choices=get_diagram_types(),
                    value="flowchart-diagram",
                    label="Diagram Type",
                    info="Select the type of diagram you want to generate"
                )
                generate_btn = gr.Button("🎨 Generate Diagram", variant="primary")
            
            with gr.Column(scale=3):
                with gr.Tabs():
                    with gr.TabItem("Rendered Image"):
                        image_output = gr.Image(label="Generated Diagram", type="filepath")
                    with gr.TabItem("Mermaid Code"):
                        code_output = gr.TextArea(
                            label="Generated Mermaid Code",
                            lines=10,
                            max_lines=30,
                            interactive=False
                        )
                    with gr.TabItem("Preview"):
                        diagram_output = gr.Markdown()
        
        with gr.Accordion("Usage Tips", open=False):
            gr.Markdown("""
            ### Tips for Better Results:
            - Be specific in your descriptions
            - Mention relationships between elements clearly
            - For flowcharts, describe the flow direction
            - For sequence diagrams, list the participants and their interactions
            - For class diagrams, specify attributes and methods
            """)
        
        generate_btn.click(
            fn=generate_and_render_diagram,
            inputs=[prompt_input, diagram_type],
            outputs=[code_output, image_output, diagram_output]
        )
        
        gr.Examples([
            ["Create a flowchart for user registration process with login, email verification, and profile setup", "flowchart-diagram"],
            ["Create a sequence diagram for an e-commerce checkout process between customer, cart, and payment system", "sequence-diagram"],
            ["Create a class diagram for a library management system with books, members, and librarians", "class-diagram"],
        ], inputs=[prompt_input, diagram_type])
    
    return app

if __name__ == "__main__":
    app = create_app()
    app.launch(server_name="0.0.0.0", server_port=7860, share=True)