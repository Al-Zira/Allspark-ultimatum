# backend/outlier_detector.py
import google.generativeai as genai
import pandas as pd
import numpy as np
from typing import List, Dict
import json

class OutlierDetector:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    def analyze_outliers(self, data: List[float], context: str = "") -> Dict:
        # Calculate statistical measures
        mean = np.mean(data)
        std = np.std(data)
        z_scores = [(x - mean) / std for x in data]
        
        # Identify potential outliers (Z-score > 2)
        outliers = [(i, value) for i, (value, z) in enumerate(zip(data, z_scores)) if abs(z) > 2]
        
        # Prepare data for Gemini analysis
        data_description = f"""
        Data summary:
        - Mean: {mean:.2f}
        - Standard deviation: {std:.2f}
        - Number of potential outliers: {len(outliers)}
        - Data points flagged as outliers: {outliers}
        
        Additional context: {context}
        """
        
        # Get AI analysis
        prompt = f"""
        Analyze the following data for outliers:
        {data_description}
        
        Please provide:
        1. An assessment of whether these are true outliers
        2. Possible explanations for the outliers
        3. Recommendations for handling these outliers
        """
        
        response = self.model.generate_content(prompt)
        
        return {
            "statistical_analysis": {
                "mean": mean,
                "std": std,
                "outlier_indices": [i for i, _ in outliers],
                "outlier_values": [v for _, v in outliers],
                "z_scores": z_scores
            },
            "ai_analysis": response.text
        }
