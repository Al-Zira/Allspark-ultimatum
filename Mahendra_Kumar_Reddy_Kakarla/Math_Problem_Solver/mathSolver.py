import streamlit as st
import google.generativeai as genai
from PIL import Image
from streamlit_drawable_canvas import st_canvas

import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model,gemini_flas_model

text_model=gemini_model()
vision_model=gemini_flas_model()





def generate_response_for_img(user_input, img):
    if user_input != "":
        prompt_template = f"""
    You are an expert mathematics problem solver. Please solve the following problem with detailed, step-by-step explanations.
    
    **Guidelines**:
    - Only solve problems related to standard, legitimate mathematics topics (such as Algebra, Geometry, Calculus, Trigonometry, Probability, etc.).
    - Avoid any problems related to speculative or unethical applications.
    - Follow all proper mathematical rules and methods in the solution.
    
    **Problem**: {user_input}
    
    **Solution**:
    -If {user_input} not related to maths then say "I'm here to help with mathematical concepts, problems, and explanations only. Please feel free to ask me any question related to Algebra, Geometry, Calculus, Trigonometry, Probability, or any other math topic. Thank you!"
        It looks like this question may not be directly related to mathematics. 
        I'm here to help with mathematical concepts, problems, and explanations only. 
        Please feel free to ask me any question related to Algebra, Geometry, Calculus, Trigonometry, Probability, or any other math topic. 
        Thank you!
    """
        response = vision_model.generate_content([prompt_template, img])
        return response.text if response else "Error generating response."
    else:
        response = vision_model.generate_content(img)
        return response.text

def generate_text_response(user_input):
    prompt_template = f"""
    You are an expert mathematics problem solver. Please solve the following problem with detailed, step-by-step explanations.
    
    **Guidelines**:
    - Only solve problems related to standard, legitimate mathematics topics (such as Algebra, Geometry, Calculus, Trigonometry, Probability, etc.).
    - Avoid any problems related to speculative or unethical applications.
    - Follow all proper mathematical rules and methods in the solution.
    
    **Problem**: {user_input}
    
    **Solution**:
    -If {user_input} not related to maths then say "I'm here to help with mathematical concepts, problems, and explanations only. Please feel free to ask me any question related to Algebra, Geometry, Calculus, Trigonometry, Probability, or any other math topic. Thank you!"
        It looks like this question may not be directly related to mathematics. 
        I'm here to help with mathematical concepts, problems, and explanations only. 
        Please feel free to ask me any question related to Algebra, Geometry, Calculus, Trigonometry, Probability, or any other math topic. 
        Thank you!
    """
    response = text_model.generate_content(prompt_template)
    return response.text if response else "Error generating response."

def main():
    st.title("MATHEMATICS PROBLEMS SOLVER")
    user_input = st.text_input("Type your question here:")

    # Create two columns for the image upload and camera input options
    col1, col2 = st.columns(2)

    with col1:
        uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

    with col2:
        st.write("Capture an image:")
        if st.button("Take a Picture"):
            camera_capture = st.camera_input("Take a picture")
        else:
            camera_capture = None  # Ensure camera_capture is None when the button is not clicked

    # Determine which image to use based on user input
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
    elif camera_capture is not None:
        image = Image.open(camera_capture)

    if image is not None:
        # Display uploaded or captured image and set up canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 0, 0, 0.3)",  # Rectangle color
            stroke_width=2,
            stroke_color="#FF0000",
            background_image=image,
            update_streamlit=True,
            height=image.height,
            width=image.width,
            drawing_mode="rect",
            key="crop_canvas",
        )

        # Check if a rectangle is drawn and crop the image
        cropped_img = None
        if canvas_result.json_data is not None:
            for shape in canvas_result.json_data["objects"]:
                if shape["type"] == "rect":
                    left = int(shape["left"])
                    top = int(shape["top"])
                    width = int(shape["width"])
                    height = int(shape["height"])
                    cropped_img = image.crop((left, top, left + width, top + height))
                    st.image(cropped_img, caption="Cropped Image", use_column_width=True)

    # Button to submit for GEMINI model response
    if st.button("Submit",use_container_width=True,type="primary"):
        if image is not None:
            img_to_use = cropped_img if cropped_img else image
            final_response = generate_response_for_img(str(user_input), img_to_use)
        elif user_input and image is None:
            final_response = generate_text_response(user_input)
        else:
            st.warning("Please enter a question or upload/capture an image.")

        st.write("Response:", final_response)

if __name__ == "__main__":
    main()
