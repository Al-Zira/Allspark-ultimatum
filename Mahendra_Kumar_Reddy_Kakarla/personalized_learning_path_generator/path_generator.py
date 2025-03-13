import gradio as gr
import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model



model = gemini_model()

# Example prompt template for Gemini model
def generate_learning_path(skill_set, interests, goals):
    prompt = f"""
    Based on the following details:
    - Skills: {skill_set}
    - Interests: {interests}
    - Goals: {goals}
    
    Generate a detailed learning path:
        1. Title of learning path
        2. Steps to learn the path
        - Each step should have a title and a description
        - Each step should have a list of sub-steps with a title and a description
            -- Each sub-step should have 2-3 resources (books, online courses, tutorials, website links, etc.) to learn the sub-step
    """
    response = model.generate_content(prompt)  # Calling the Gemini model to generate the learning path
    return response.text.strip()  # Returning the generated learning path


# Save learning path function (to download as markdown)
def save_as_markdown(learning_path, file_name):
    os.makedirs("learning_paths", exist_ok=True)  # Ensure folder exists
    file_path = f"learning_paths/{file_name}.md"
    with open(file_path, "w") as f:
        f.write(learning_path)
    return file_path  # Returning file path to allow download


# Gradio Interface
def app():
    with gr.Blocks() as demo:
        gr.Markdown("## AI Learning Path Generator")

        # Inputs for new learning path generation
        with gr.Row():
            skill_input = gr.Textbox(label="Enter your skills (comma-separated)", placeholder="e.g., Python, Machine Learning")
            interest_input = gr.Textbox(label="Enter your interests (comma-separated)", placeholder="e.g., AI, Robotics")
            goal_input = gr.Textbox(label="Enter your goals", placeholder="e.g., Get a job in AI")

        generate_button = gr.Button("Generate Learning Path")
        learning_path_output = gr.Markdown(label="Generated Learning Path")
        file_name_input = gr.Textbox(label="Enter filename to save (without extension)", placeholder="e.g., learning_path")
        download_button = gr.Button("Download Learning Path")

        # Generate button logic
        generate_button.click(
            lambda skill, interest, goal: generate_learning_path(skill.split(','), interest.split(','), goal),
            inputs=[skill_input, interest_input, goal_input],
            outputs=learning_path_output
        )

        # Download button logic (save as markdown and return file path)
        download_button.click(
            lambda path, file_name: save_as_markdown(path, file_name),
            inputs=[learning_path_output, file_name_input],
            outputs=gr.File()  # Gradio file component for downloading the file
        )

    return demo


demo = app()
demo.launch(debug=True, share=True,allowed_paths=["learning_paths"])
