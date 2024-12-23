import gradio as gr
import json

import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model
import google.generativeai as genai

model = gemini_model()

# Example prompt template for Gemini model
def generate_learning_path(skill_set, interests, goals):
    prompt = f"""
    Based on the following details:
    - Skills: {skill_set}
    - Interests: {interests}
    - Goals: {goals}
    
    Generate a detailed learning path. Break it down into steps and organize them as a to-do list.
    if there is any courses or books is there give 3-4 recommendations for each step along with links if available.
    """
    # Replace this with the actual Gemini API call
    # Here, simulating a response
    response = model.generate_content(prompt)
    
    return response.text.strip()

# Save learning path with custom file name
def save_learning_path(learning_path, file_name):
    with open(f"{file_name}.json", "w") as f:
        json.dump({"learning_path": learning_path}, f)
    return f"Learning path saved successfully as {file_name}.json!"



# Gradio Interface
def app():
    with gr.Blocks() as demo:
        gr.Markdown("## AI Learning Path Generator")
        
        with gr.Row():
            skill_input = gr.Textbox(label="Enter your skills (comma-separated)", placeholder="e.g., Python, Machine Learning")
            interest_input = gr.Textbox(label="Enter your interests (comma-separated)", placeholder="e.g., AI, Robotics")
            goal_input = gr.Textbox(label="Enter your goals", placeholder="e.g., Get a job in AI")
        
        generate_button = gr.Button("Generate Learning Path")
        learning_path_output = gr.Markdown(label="Your Learning Path")
        
        file_name_input = gr.Textbox(label="Enter filename to save (without extension)", placeholder="e.g., learning_path")
        
        save_button = gr.Button("Save Learning Path")
        save_status = gr.Markdown(label="Save Status")
        
        
        
        generate_button.click(
            lambda skill, interest, goal: generate_learning_path(skill.split(','), interest.split(','), goal),
            inputs=[skill_input, interest_input, goal_input],
            outputs=learning_path_output
        )
        
        save_button.click(
            lambda path, file_name: save_learning_path(path, file_name),
            inputs=[learning_path_output, file_name_input],
            outputs=save_status
        )
        
        
    return demo

demo = app()
demo.launch(debug=True, share=True)
