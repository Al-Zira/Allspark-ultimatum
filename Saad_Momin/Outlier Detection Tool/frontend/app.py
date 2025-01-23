import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
from io import StringIO

st.set_page_config(page_title="Outlier Detection Tool", layout="wide")

def create_visualization(data, outlier_indices, column_name="Values"):
    fig = go.Figure()
    
    # Add regular points
    regular_indices = [i for i in range(len(data)) if i not in outlier_indices]
    fig.add_trace(go.Scatter(
        x=regular_indices,
        y=[data[i] for i in regular_indices],
        mode='markers',
        name='Regular Points',
        marker=dict(color='blue')
    ))
    
    # Add outlier points
    if outlier_indices:
        fig.add_trace(go.Scatter(
            x=outlier_indices,
            y=[data[i] for i in outlier_indices],
            mode='markers',
            name='Outliers',
            marker=dict(color='red', size=10)
        ))
    
    fig.update_layout(
        title=f'Data Points Distribution - {column_name}',
        xaxis_title='Index',
        yaxis_title='Value',
        showlegend=True
    )
    
    return fig

st.title("Outlier Detection Tool")

st.header("File Upload")
uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
context = st.text_area(
    "Additional context (optional):",
    value=""
)

if uploaded_file and st.button("Analyze"):
    try:
        # Create a named temporary file-like object
        files = {
            "file": ("filename.csv", uploaded_file.getvalue(), "text/csv")
        }
        data = {"context": context}
        
        response = requests.post(
            "http://localhost:8000/analyze_file",
            files=files,
            data=data
        )
        
        if response.status_code == 200:
            results = response.json()
            
            # Read the data once for visualization
            df = pd.read_csv(StringIO(uploaded_file.getvalue().decode('utf-8')))
            
            for column, result in results.items():
                st.subheader(f"Analysis for column: {column}")
                
                # Display visualization
                st.plotly_chart(create_visualization(
                    df[column].tolist(),
                    result["statistical_analysis"]["outlier_indices"],
                    column
                ))
                
                # Display statistical analysis
                st.write("Statistical Analysis")
                st.write(f"Mean: {result['statistical_analysis']['mean']:.2f}")
                st.write(f"Standard Deviation: {result['statistical_analysis']['std']:.2f}")
                st.write(f"Number of outliers: {len(result['statistical_analysis']['outlier_indices'])}")
                
                # Display AI analysis
                st.write("AI Analysis")
                st.write(result["ai_analysis"])
                
                st.markdown("---")
                
    except Exception as e:
        st.error(f"Error: {str(e)}")