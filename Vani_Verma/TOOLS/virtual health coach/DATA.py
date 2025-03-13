import os
import gradio as gr
import plotly.graph_objects as go
import numpy as np
import re
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the API key (if needed for external API calls)
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found. You can add it to your .env file if you need external data.")

# Function to generate interactive visualizations using Plotly
def generate_visualizations(prompt):
    """
    Generates interactive plots based on the provided prompt.
    """
    try:
        # Default values
        chart_type = None
        x_data = []
        y_data = []
        x_label = "X Axis"
        y_label = "Y Axis"
        color = 'blue'

        # Step 1: Parse the prompt for the chart type and data specifics
        if "bar chart" in prompt.lower():
            chart_type = 'Bar Chart'
        elif "line chart" in prompt.lower():
            chart_type = 'Line Chart'
        elif "scatter plot" in prompt.lower():
            chart_type = 'Scatter Plot'
        elif "pie chart" in prompt.lower():
            chart_type = 'Pie Chart'
        elif "box plot" in prompt.lower():
            chart_type = 'Box Plot'
        elif "histogram" in prompt.lower():
            chart_type = 'Histogram'
        elif "heatmap" in prompt.lower():
            chart_type = 'Heatmap'
        elif "area chart" in prompt.lower():
            chart_type = 'Area Chart'
        elif "violin plot" in prompt.lower():
            chart_type = 'Violin Plot'
        else:
            return "Error: Could not detect a valid chart type in the prompt."

        # Step 2: Identify data domain and axis labels
        # Example: Rainfall data, Sales, Temperature, etc.
        if "rainfall" in prompt.lower():
            data_domain = "Rainfall"
        elif "sales" in prompt.lower():
            data_domain = "Sales"
        elif "temperature" in prompt.lower():
            data_domain = "Temperature"
        else:
            data_domain = "General Data"

        # Step 3: Extract year range and x-axis categories (e.g., states, months)
        range_match = re.search(r"from (\d{4}) to (\d{4})", prompt)
        if range_match:
            start_year, end_year = int(range_match.group(1)), int(range_match.group(2))
            y_data = list(range(start_year, end_year + 1))
        else:
            return "Error: Could not detect valid year range for data."

        # Step 4: Extract X-axis categories (e.g., states, months, etc.)
        if "states" in prompt.lower():
            x_data = ["Kerala", "Maharashtra", "Uttar Pradesh", "Tamil Nadu", "West Bengal"]
            x_label = "States"
        elif "months" in prompt.lower():
            x_data = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"]
            x_label = "Months"
        elif "countries" in prompt.lower():
            x_data = ["USA", "Canada", "India", "Australia", "UK"]
            x_label = "Countries"
        else:
            x_data = ["Category 1", "Category 2", "Category 3"]
            x_label = "Categories"

        # Step 5: Generate random data for the specified domain (e.g., rainfall, sales, etc.)
        if data_domain == "Rainfall":
            # Generate random rainfall data (mm) for the years
            y_data_values = np.random.randint(500, 3000, size=(len(x_data), len(y_data)))  # Random rainfall data
            y_label = "Annual Rainfall (mm)"
        elif data_domain == "Sales":
            # Generate random sales data for each category
            y_data_values = np.random.randint(1000, 5000, size=(len(x_data), len(y_data)))  # Random sales data
            y_label = "Sales (Units)"
        elif data_domain == "Temperature":
            # Generate random temperature data (°C) for each category
            y_data_values = np.random.randint(-10, 40, size=(len(x_data), len(y_data)))  # Random temperature data
            y_label = "Temperature (°C)"
        else:
            # General random data
            y_data_values = np.random.rand(len(x_data), len(y_data)) * 100
            y_label = "Y Axis"

        # Step 6: Generate the plot based on the chart type
        fig = go.Figure()

        if chart_type == 'Line Chart':
            for i, state in enumerate(x_data):
                fig.add_trace(go.Scatter(x=y_data, y=y_data_values[i], mode='lines+markers', name=state))
            fig.update_layout(title="Line Chart", xaxis_title=x_label, yaxis_title=y_label)
        elif chart_type == 'Bar Chart':
            fig.add_trace(go.Bar(x=x_data, y=y_data_values.flatten(), name='Bar Chart', marker=dict(color=color)))
            fig.update_layout(title="Bar Chart", xaxis_title=x_label, yaxis_title=y_label)
        elif chart_type == 'Scatter Plot':
            for i, state in enumerate(x_data):
                fig.add_trace(go.Scatter(x=y_data, y=y_data_values[i], mode='markers', name=state))
            fig.update_layout(title="Scatter Plot", xaxis_title=x_label, yaxis_title=y_label)
        elif chart_type == 'Pie Chart':
            fig.add_trace(go.Pie(labels=x_data, values=y_data_values.flatten(), hole=0.3))
            fig.update_layout(title="Pie Chart")
        elif chart_type == 'Box Plot':
            fig.add_trace(go.Box(y=y_data_values.flatten(), name='Box Plot'))
            fig.update_layout(title="Box Plot", yaxis_title=y_label)
        elif chart_type == 'Histogram':
            fig.add_trace(go.Histogram(x=y_data_values.flatten(), name='Histogram', marker=dict(color=color)))
            fig.update_layout(title="Histogram", xaxis_title=x_label, yaxis_title="Frequency")
        elif chart_type == 'Heatmap':
            fig.add_trace(go.Heatmap(z=y_data_values, colorscale='YlGnBu'))
            fig.update_layout(title="Heatmap")
        elif chart_type == 'Area Chart':
            fig.add_trace(go.Scatter(x=x_data, y=y_data_values.flatten(), fill='tozeroy', name='Area Chart', line=dict(color=color)))
            fig.update_layout(title="Area Chart", xaxis_title=x_label, yaxis_title=y_label)
        elif chart_type == 'Violin Plot':
            fig.add_trace(go.Violin(y=y_data_values.flatten(), box_visible=True, line_color=color, name='Violin Plot'))
            fig.update_layout(title="Violin Plot", yaxis_title=y_label)

        fig.update_layout(template="plotly", showlegend=True)
        return fig

    except Exception as e:
        return f"Error: {str(e)}"

# Gradio Interface to interact with the user and generate the plot
def gradio_interface(prompt):
    """
    Handles the user input and triggers the appropriate chart generation based on the prompt.
    """
    return generate_visualizations(prompt)

# Gradio Interface Setup
iface = gr.Interface(
    fn=gradio_interface,
    inputs=[
        gr.Textbox(label="Enter Prompt", placeholder="e.g. Generate a line chart showing sales from 2015-2020")
    ],
    outputs="plot",  # Output will be a plot
    live=False,  # Disable live updates, only update when the user clicks 'Submit'
    title="Comprehensive Data Visualization Tool",
    description="Generate a [chart type] to show the relationship between [x-axis data] and [y-axis data], with [optional specifications]."
)

# Launch Gradio App
iface.launch()
