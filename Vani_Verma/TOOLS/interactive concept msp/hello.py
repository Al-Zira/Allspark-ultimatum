import os
import gradio as gr
import google.generativeai as genai
import networkx as nx
import plotly.graph_objects as go
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("Gemini API key not found. Please set GEMINI_API_KEY in your .env file.")

# Configure the Google Generative AI API with the provided API key
genai.configure(api_key=api_key)

# Define the models to use
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config={
        "temperature": 0.9,
        "top_p": 1.0,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
    }
)

flash_model = genai.GenerativeModel(
    model_name="gemini-flash-1.5",
    generation_config={
        "temperature": 0.7,
        "top_p": 1.0,
        "max_output_tokens": 1024,
        "response_mime_type": "application/json",
    }
)

# Function to generate concept map data
def generate_concept_map(keyword):
    prompt = f"""
    Given the keyword: '{keyword}', generate a structured concept map.
    Identify key concepts related to this keyword and define their relationships.
    Respond strictly in JSON format with no additional text. Only return:
    {{
        "nodes": [
            {{"name": "{keyword}"}},
            {{"name": "Subtopic1"}},
            {{"name": "Subtopic2"}}
        ],
        "edges": [
            {{"source": "{keyword}", "target": "Subtopic1"}},
            {{"source": "{keyword}", "target": "Subtopic2"}}
        ]
    }}
    """
    
    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        print("Raw Gemini Response:", response_text)  # Debugging output

        # Ensure only JSON is parsed
        if response_text.startswith("{") and response_text.endswith("}"):
            response_json = json.loads(response_text)
        else:
            raise ValueError("Invalid JSON format received from API")
        
        nodes = {node["name"] for node in response_json.get("nodes", [])}
        edges = [(edge["source"], edge["target"]) for edge in response_json.get("edges", [])]
        
        return nodes, edges
    except Exception as e:
        print("Error parsing response:", e)
        return set(), []  # Return empty graph data on error

# Function to visualize the concept map
def generate_visualization(keyword):
    nodes, edges = generate_concept_map(keyword)
    
    G = nx.Graph()
    G.add_nodes_from(nodes)
    G.add_edges_from(edges)
    
    pos = nx.spring_layout(G)
    edge_x, edge_y = [], []
    
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color='black'),
        hoverinfo='none',
        mode='lines'
    )
    
    node_x, node_y, node_text = [], [], []
    for node in nodes:
        x, y = pos[node]
        node_x.append(x)
        node_y.append(y)
        node_text.append(node)
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        marker=dict(size=10, color='skyblue'),
        text=node_text,
        textposition='top center',
        hoverinfo='text'
    )
    
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title="Generated Concept Map",
        showlegend=False,
        hovermode='closest',
        margin=dict(b=0, l=0, r=0, t=40),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
    )
    
    return fig

# Gradio interface
def gradio_interface(keyword):
    return generate_visualization(keyword)

iface = gr.Interface(
    fn=gradio_interface,
    inputs=[gr.Textbox(label="Enter a Keyword")],
    outputs=gr.Plot(label="Concept Map Output"),
    title="Concept Map Generator",
    description="Enter a single word or short phrase to generate a concept map."
)

iface.launch()