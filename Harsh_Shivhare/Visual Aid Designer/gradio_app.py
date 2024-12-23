import gradio as gr
import tempfile
from diagram_generator import generate_mermaid_code
from mermaid_renderer import MermaidRenderer

DIAGRAM_TYPES = [
    "flowchart-diagram", "sequence-diagram", "class-diagram", "state-diagram",
    "entity-relationship-diagram", "gantt-diagram", "pie-chart", "quadrant-chart",
    "reqirement-diagram", "timeline-diagram", "git-diagram", "mind-map-diagram"
]

renderer = MermaidRenderer()

def generate_and_render_diagram(prompt, diagram_type):
    try:
        mermaid_code = generate_mermaid_code(diagram_type, prompt)
        
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as temp_file:
            output_path = temp_file.name
        
        success = renderer.render_diagram(mermaid_code, output_path)
        return mermaid_code, output_path if success else None, f"```mermaid\n{mermaid_code}\n```"
    except Exception as e:
        return str(e), None, ""

with gr.Blocks(title="Visual Aid Designer", theme=gr.themes.Soft()) as app:
    gr.Markdown("# 🎨 Visual Aid Designer\n\nGenerate beautiful diagrams from text descriptions this Tool!")
    
    with gr.Row():
        with gr.Column(scale=2):
            prompt_input = gr.Textbox(
                label="Diagram Description",
                placeholder="Describe the diagram you want to create...",
                lines=5
            )
            diagram_type = gr.Dropdown(
                choices=DIAGRAM_TYPES,
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

if __name__ == "__main__":
    app.launch(share=True)