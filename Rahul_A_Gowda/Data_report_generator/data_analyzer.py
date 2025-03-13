import pandas as pd
import numpy as np
from typing import Dict, List
import json

class DataAnalyzer:
    def __init__(self, csv_path: str):
        self.df = pd.read_csv(csv_path)
        self.analysis_results = {}

    def perform_analysis(self) -> Dict:
        """Perform comprehensive analysis of the CSV data"""
        analysis = {
            "basic_stats": self._get_basic_stats(),
            "correlations": self._get_correlations(),
            "missing_data": self._get_missing_data_info(),
            "unique_values": self._get_unique_values(),
            "data_types": self._get_data_types()
        }
        self.analysis_results = analysis
        return analysis

    def _get_basic_stats(self) -> Dict:
        """Get basic statistical information"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        stats = self.df[numeric_cols].describe().to_dict()
        return {col: {k: float(v) for k, v in values.items()} 
                for col, values in stats.items()}

    def _get_correlations(self) -> Dict:
        """Calculate correlations between numeric columns"""
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 1:
            corr = self.df[numeric_cols].corr().to_dict()
            return {col: {k: float(v) for k, v in values.items()} 
                    for col, values in corr.items()}
        return {}

    def _get_missing_data_info(self) -> Dict:
        """Get information about missing data"""
        missing = self.df.isnull().sum().to_dict()
        return {col: int(count) for col, count in missing.items()}

    def _get_unique_values(self) -> Dict:
        """Get unique value counts for each column"""
        return {col: len(self.df[col].unique()) for col in self.df.columns}

    def _get_data_types(self) -> Dict:
        """Get data types of each column"""
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    def generate_detailed_sections(self) -> List[str]:
        """Generate detailed sections for context"""
        sections = []
        
        # Basic Information Section
        sections.append(f"Dataset Overview:\n"
                       f"Total Records: {len(self.df)}\n"
                       f"Total Features: {len(self.df.columns)}\n"
                       f"Columns: {', '.join(self.df.columns)}")

        # Statistical Analysis Section
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            stats = self.df[col].describe()
            sections.append(f"\nMetrics for {col}:\n"
                          f"Average: {stats['mean']:.2f}\n"
                          f"Range: {stats['min']:.2f} to {stats['max']:.2f}\n"
                          f"Standard Deviation: {stats['std']:.2f}")

        # Correlation Insights
        if len(numeric_cols) > 1:
            correlations = self.df[numeric_cols].corr()
            strong_correlations = []
            for i in range(len(numeric_cols)):
                for j in range(i+1, len(numeric_cols)):
                    corr = correlations.iloc[i, j]
                    if abs(corr) > 0.5:
                        strong_correlations.append(
                            f"{numeric_cols[i]} and {numeric_cols[j]}: {corr:.2f}")
            if strong_correlations:
                sections.append("\nSignificant Correlations:\n" + 
                              "\n".join(strong_correlations))

        # Missing Data Analysis
        missing = self.df.isnull().sum()
        if missing.any():
            missing_info = [f"{col}: {count} missing values"
                          for col, count in missing.items() if count > 0]
            sections.append("\nMissing Data Summary:\n" + 
                          "\n".join(missing_info))

        return sections

    def get_context_string(self) -> str:
        """Generate a complete context string for the LLM"""
        sections = self.generate_detailed_sections()
        return "\n\n".join(sections)

    def get_analysis_summary(self) -> str:
        """Convert analysis results to a readable summary"""
        if not self.analysis_results:
            self.perform_analysis()
            
        summary = []
        summary.append("Data Analysis Summary:")
        summary.append("\n1. Basic Information:")
        summary.append(f"- Total rows: {len(self.df)}")
        summary.append(f"- Total columns: {len(self.df.columns)}")
        
        summary.append("\n2. Missing Data:")
        for col, count in self.analysis_results['missing_data'].items():
            if count > 0:
                summary.append(f"- {col}: {count} missing values")
        
        summary.append("\n3. Numeric Columns Statistics:")
        for col, stats in self.analysis_results['basic_stats'].items():
            summary.append(f"\n{col}:")
            summary.append(f"- Mean: {stats['mean']:.2f}")
            summary.append(f"- Std: {stats['std']:.2f}")
            summary.append(f"- Min: {stats['min']:.2f}")
            summary.append(f"- Max: {stats['max']:.2f}")
        
        return "\n".join(summary)