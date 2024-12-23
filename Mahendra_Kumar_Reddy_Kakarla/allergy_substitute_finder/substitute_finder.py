import gradio as gr
import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model

model = gemini_model()  # Ensure the Gemini Pro model is properly integrated

# Function to get substitutes from the Gemini Pro model
def gemini_response(allergy_items, situation):
    prompt = f"""Suggest substitutes for the following allergy items: {allergy_items}. 
    Situation: {situation}.
    Provide a brief explanation for each substitute in a table format with the columns: Allergy Item, Substitute, Explanation."""
    response = model.generate_content(prompt)  # Using the Gemini Pro model to generate substitutes
    return response.text

# Create the Gradio interface with input textboxes, button, and output
def create_interface():
    # Textboxes for entering allergy items and situation
    allergy_input = gr.Textbox(
        label="Allergy Items",
        placeholder="Enter allergy items separated by commas (e.g., peanuts, dairy, gluten)",
        lines=1
    )
    situation_input = gr.Textbox(
        label="Situation",
        placeholder="Describe the situation (e.g., dinner party, outdoor event, etc.)",
        lines=1
    )
    
    # Button to trigger the function
    find_button = gr.Button("Find Substitutes")
    
    # Output area for showing the substitutes (Markdown)
    output = gr.Markdown(label="Suggested Substitutes")

    # Set up the interface with a title and description
    with gr.Blocks() as iface:
        gr.Markdown("# Allergy Item Substitutes Generator")
        gr.Markdown("Enter allergy items and a situation to get suggestions for potential substitutes.")
        
        # Create a layout with left and right halves
        with gr.Row():
            # Left half with input fields and button
            with gr.Column(scale=1):
                with gr.Row():
                    allergy_input.render()
                    situation_input.render()
                find_button.render()
            
            # Right half with output
            with gr.Column(scale=1):
                output.render()
        
        # Set the button click functionality
        find_button.click(fn=gemini_response, inputs=[allergy_input, situation_input], outputs=output)

    return iface

# Launch the interface
iface = create_interface()
iface.launch()
