import gradio as gr
from pyzbar.pyzbar import decode
from PIL import Image
import requests
import os
import sys

script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

sys.path.append(script_path)

from geminiModel import gemini_model,gemini_flas_model


model = gemini_model()
flash_model = gemini_flas_model()

def get_nutrios_facts(productName,companyName,descripiton):
    prompt=f"As a nutritional expert, please extract the nutritional facts from the following product information using reliable online sources and your knowledge of well-known brands' nutrition profiles:\n\nProduct Name: {productName}\nCompany Name: {companyName}\nDescription: {descripiton}\n\nIf specific nutritional information is not available from these sources, provide general nutritional information for the product, including calories, fat, carbs, protein, sugar, sodium, and fiber content. If any of these values are not available, please indicate 'Not available'.\n\nFor example:\n- Calories: Not available\n- Fat: Not available\n- Carbs: Not available\n- Protein: Not available\n- Sugar: Not available\n- Sodium: Not available\n- Fiber: Not available"
    response=model.generate_content(prompt)
    return response.text



# Example function for Gemini Pro nutrition fact model (assuming you have it accessible)
def get_nutrition_facts(product_info, image=None):
    print("info:", product_info)
    """
    Pass the product info to Gemini Pro model to get nutritional facts.
    This is a placeholder function and should be replaced with actual API calls to Gemini Pro.
    """
    if image:
        # Assuming Gemini Flash model can process images directly to extract nutrition facts
        prompt = f"""
As a nutritional expert, please extract the nutritional facts from the following product information using reliable online sources and your knowledge of well-known brands' nutrition profiles:

{product_info}

If specific nutritional information is not available from these sources, provide general nutritional information for the product, including calories, fat, carbs, protein, sugar, sodium, and fiber content. If any of these values are not available, please indicate "Not available".

For example:
- Calories: Not available
- Fat: Not available
- Carbs: Not available
- Protein: Not available
- Sugar: Not available
- Sodium: Not available
- Fiber: Not available
"""

        response = flash_model.generate_content([prompt, image])
        return response.text
    else:
        # For text-based product info, use the regular Gemini model
        prompt = f"""
As a nutritional expert, please extract the nutritional facts from the following product information using reliable online sources and your knowledge of well-known brands' nutrition profiles:

{product_info}

If specific nutritional information is not available from these sources, provide general nutritional information for the product, including calories, fat, carbs, protein, sugar, sodium, and fiber content. If any of these values are not available, please indicate "Not available".

For example:
- Calories: Not available
- Fat: Not available
- Carbs: Not available
- Protein: Not available
- Sugar: Not available
- Sodium: Not available
- Fiber: Not available
"""
        response = model.generate_content(prompt)
        return response.text


def fetch_product_info(barcode):
    """
    Fetch product details from Open Food Facts API based on the barcode.
    """
    url = f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json"
    response = requests.get(url)

    if response.status_code == 200:
        product_data = response.json()
        if product_data.get("product"):
            product = product_data["product"]

            # Extracting product details
            name = product.get("product_name", "No name available")
            description = product.get("ingredients_text", "No description available")
            company = product.get("manufacturer_name", "No manufacturer information available")
            code = product.get("code", "No barcode found")
            packaging = product.get("packaging", "No packaging information available")
            quantity = product.get("quantity", "No quantity information available")
            labels = product.get("labels", "No label information available")
            categories = product.get("categories", "No categories available")

            product_info = f"""Name: {name}
Description: {description}
Company: {company}
Barcode: {code}
Packaging: {packaging}
Quantity: {quantity}
Labels: {labels}
Categories: {categories}
"""
            # Pass product info to Gemini Pro model for nutrition facts
            nutrition_facts = get_nutrition_facts(product_info)
            return f"{product_info}\n\nNutrition Facts:\n{nutrition_facts}"
        else:
            return "Product not found in the Open Food Facts database."
    else:
        return "Failed to retrieve product information. Please try again later."


def decode_barcode_or_qr(image):
    """
    Decode barcode or QR code from the uploaded image and fetch product details.
    If the image doesn't contain a barcode, it will return None for further processing.
    """
    # Decode barcodes or QR codes using pyzbar
    decoded_objects = decode(image)
    if not decoded_objects:
        return None  # Return None if no barcode or QR code is found

    # Extract product info for each decoded barcode
    results = []
    for obj in decoded_objects:
        barcode_data = obj.data.decode("utf-8")
        # Fetch product details from Open Food Facts API
        product_info = fetch_product_info(barcode_data)
        results.append(f"Barcode: {barcode_data}\n{product_info}")

    return "\n\n".join(results)


def process_image(image):
    """
    Process the uploaded image.
    If the image contains a barcode or QR code, extract product info.
    Otherwise, send it to the Gemini Flash model for nutrition facts.
    """
    # Convert to Pillow image if necessary
    if isinstance(image, Image.Image):
        barcode_info = decode_barcode_or_qr(image)
    
        if barcode_info:
            return barcode_info  # If barcode or QR code is detected, return the info
    
        # If no barcode, send the image to the Gemini Flash model for nutrition facts
        nutrition_facts = get_nutrition_facts(None, image=image)
        return f"Nutrition Facts extracted from the image: \n{nutrition_facts}"
    else:
        return "Invalid image format. Please upload a valid image."


# Gradio Interface
with gr.Blocks() as barcode_decoder_app:
    gr.Markdown("# Product Info and Nutrition Checker")
    gr.Markdown("### Upload a barcode or QR code image, or a regular image to get nutrition facts.")

    # Tabs for input
    with gr.Tabs():
        with gr.Tab("Image Upload"):
            # Tab for uploading image
            image_input = gr.Image(type="pil", label="Upload Barcode/QR Code or Normal Image")
            nutrition_button = gr.Button("Get Nutrition Facts")
            nutrition_output = gr.Markdown(label="Product Information and Nutrition Facts")

            # When the button is clicked, process the image and provide the output
            nutrition_button.click(fn=process_image, inputs=image_input, outputs=nutrition_output)

        with gr.Tab("Product Info Upload"):
            # Tab for entering product details manually
            product_name = gr.Textbox(label="Product Name", placeholder="Enter the product name", lines=1)
            company_name = gr.Textbox(label="Company Name", placeholder="Enter the company name", lines=1)
            description = gr.Textbox(label="Description", placeholder="Enter product description", lines=3)
            nutrition_button2 = gr.Button("Get Nutrition Facts")
            nutrition_output2 = gr.Textbox(label="Nutrition Facts", lines=8)

            # When the button is clicked, generate nutrition facts from the entered product info
            nutrition_button2.click(fn=get_nutrios_facts, inputs=[product_name, company_name, description], outputs=nutrition_output2)

barcode_decoder_app.launch()
