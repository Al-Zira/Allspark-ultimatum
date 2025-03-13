# backend/api.py
from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List
import pandas as pd
import json
import numpy as np
from io import StringIO
import os
import sys

# Add the project root to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.append(project_root)

from backend.outlier_detector import OutlierDetector
from backend.config import GEMINI_API_KEY

app = FastAPI()
detector = OutlierDetector(GEMINI_API_KEY)

class DataInput(BaseModel):
    data: List[float]
    context: str = ""

def should_analyze_column(df: pd.DataFrame, column: str) -> bool:
    series = df[column]
    
    # Skip if more than 30% values are missing
    if series.isnull().mean() > 0.3:
        return False
    
    # Explicitly identify binary/categorical columns
    if set(series.dropna().unique()).issubset({0, 1}):
        return False
        
    # Skip if column has very few unique values relative to its length (likely categorical)
    unique_ratio = len(series.unique()) / len(series)
    if unique_ratio < 0.05 and len(series.unique()) < 10:  # Modified condition
        return False
    
    # Skip if column has very low variance
    if series.std() == 0 or series.var() < 1e-10:
        return False
    
    # Skip if column name suggests it's an ID (common patterns)
    id_patterns = ['id', 'index', 'key', 'code']
    if any(pattern in column.lower() for pattern in id_patterns):
        return False
    
    # Always include important financial/demographic columns
    important_patterns = ['credit', 'score', 'salary', 'income', 'balance', 'age']
    if any(pattern in column.lower() for pattern in important_patterns):
        return True
    
    return True

@app.post("/analyze_outliers")
async def analyze_outliers(data_input: DataInput):
    try:
        result = detector.analyze_outliers(data_input.data, data_input.context)
        return result
    except Exception as e:
        return {"error": str(e)}

@app.post("/analyze_file")
async def analyze_file(file: UploadFile = File(...), context: str = ""):
    try:
        # Read the file content
        contents = await file.read()
        # Convert to string and create DataFrame
        df = pd.read_csv(StringIO(contents.decode('utf-8')))
        
        # Get numeric columns and filter them
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        columns_to_analyze = [col for col in numeric_columns if should_analyze_column(df, col)]
        
        # Get dataset context for better AI analysis
        dataset_context = f"""
        This analysis is for a dataset with {len(df)} rows and the following columns:
        {', '.join(df.columns)}
        
        Overall dataset statistics:
        - Total features: {len(df.columns)}
        - Numeric features: {len(numeric_columns)}
        - Selected features for outlier analysis: {len(columns_to_analyze)}
        
        {context}
        """
        
        results = {}
        for column in columns_to_analyze:
            # Calculate percentiles for better context
            percentiles = df[column].quantile([0.25, 0.5, 0.75]).to_dict()
            
            column_context = f"""
            Analysis for column: {column}
            
            Column type: {df[column].dtype}
            Column statistics:
            - Count: {df[column].count()}
            - Unique values: {len(df[column].unique())}
            - Missing values: {df[column].isnull().sum()}
            - Data range: {df[column].min()} to {df[column].max()}
            - 25th percentile: {percentiles[0.25]:.2f}
            - Median: {percentiles[0.5]:.2f}
            - 75th percentile: {percentiles[0.75]:.2f}
            
            Dataset context: {dataset_context}
            """
            
            results[column] = detector.analyze_outliers(
                df[column].dropna().tolist(),
                column_context
            )
        
        return results
    except Exception as e:
        return {"error": str(e)}
