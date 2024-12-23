import gradio as gr
import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model,gemini_flas_model


# Initialize the Gemini model
gemini_pro_model = gemini_model()
image_summary_model = gemini_flas_model()

# Function to fetch resources based on a topic
def find_resources(topic):
    if not topic.strip():
        return "Please enter a valid topic."
    prompt = f"List all the useful resources, articles, youtube videos, and links related to the topic: \"{topic}\" in markdown format."
    response = gemini_pro_model.generate_content(prompt)
    return response.text if response else "No resources found."

# Function to generate MCQ test from prompt
def generate_test(prompt):
    if not prompt.strip():
        return "Please enter a valid prompt."
    test_prompt = f"Generate a multiple-choice and oneline and fill in th blacks test with some questions only based on the following prompt: \"{prompt}\" in markdown format."


    response = gemini_pro_model.generate_content(test_prompt)
    return response.text if response else "No test generated."

# Function to evaluate the answers
def evaluate_answers(user_answers, test):
    prompt=f"Evalueate the answers of the user and give the score. Also give the correct answers. Here is the test: {test} and here are the user answers: {user_answers}"
    response=gemini_pro_model.generate_content(prompt)

    
    return response.text
# Gradio Interface
with gr.Blocks() as demo:
    gr.Markdown("# AI Powered Study Assistant")

    with gr.Tabs():
        # Summarization tab
        with gr.Tab("Summarization"):
            with gr.Row():
                input_type = gr.Dropdown(
                    ["Text", "Images"],
                    label="Select Input Type",
                    value="Text"
                )
            
            with gr.Row():
                text_area = gr.TextArea(label="Enter Text", visible=True, placeholder="Type text to summarize...")
                image_upload = gr.Image(label="Upload Image", visible=False, type="filepath")
                prompt_text = gr.Textbox(label="Enter Custom Prompt", placeholder="Optional custom prompt...", visible=True)
            
            with gr.Row():
                summarize_button = gr.Button("Summarize")

            output_text = gr.Markdown()

            # Dynamic visibility based on input type
            def update_input_visibility(selected_type):
                return (
                    gr.update(visible=(selected_type == "Text")),
                    gr.update(visible=(selected_type == "Images")),
                    gr.update(visible=True)  # Always show prompt for both Text and Images
                )
            
            input_type.change(
                update_input_visibility,
                inputs=[input_type],
                outputs=[text_area, image_upload, prompt_text]
            )

            # Summarization logic
            def summerizer(input_data, input_type, image_data=None, custom_prompt=None):
                response = None
                
                if input_type == "Text":
                    prompt = custom_prompt +":"+f"Summarize the following text in bullet points: \"{input_data}\""
                    response = gemini_pro_model.generate_content(prompt)
                elif input_type == "Images":
                    try:
                        from PIL import Image
                        image = Image.open(image_data)
                        prompt = custom_prompt or "Summarize the content of the uploaded image."
                        response = image_summary_model.generate_content([prompt, image])
                    except Exception as e:
                        return f"Error processing the image: {str(e)}"
                
                return response.text if response else "No response generated."

            summarize_button.click(
                summerizer,
                inputs=[text_area, input_type, image_upload, prompt_text],
                outputs=[output_text]
            )

        # Resources tab
        with gr.Tab("Find Resources"):
            with gr.Row():
                topic_input = gr.TextArea(label="Enter Topic", placeholder="Type a topic to find resources...")
            
            with gr.Row():
                find_button = gr.Button("Find Resources")

            resources_output = gr.Markdown()

            # Fetch resources
            find_button.click(
                find_resources,
                inputs=[topic_input],
                outputs=[resources_output]
            )

        # Tester tab
        with gr.Tab("Tester"):
            with gr.Row():
                prompt_input = gr.Textbox(label="Enter Topic or Prompt", placeholder="Type a topic to generate a test...")

            with gr.Row():
                generate_test_button = gr.Button("Generate Test")

            test_output = gr.Markdown()
            answer_input = gr.Textbox(label="Enter your answers (comma-separated)", placeholder="Enter answers here...")

            evaluation_button = gr.Button("Evaluate Answers")
            evaluation_output = gr.Markdown()

            # Generate MCQ test
            generate_test_button.click(
                generate_test,
                inputs=[prompt_input],
                outputs=[test_output]
            )

            # Evaluate answers
            evaluation_button.click(
                evaluate_answers,
                inputs=[answer_input, test_output],
                outputs=[evaluation_output]
            )

demo.launch()
