# File: src/report_generator.py
import os
from datetime import datetime
from typing import List, Dict
import json

class RedactionReportGenerator:
    def create_report(
        self, 
        original_file: str, 
        redacted_file: str, 
        suggestions: List[Dict]
    ) -> str:
        """
        Generate a comprehensive redaction report
        
        Args:
            original_file (str): Path to original file
            redacted_file (str): Path to redacted file
            suggestions (List[Dict]): Redaction suggestions applied
        
        Returns:
            str: Redaction report content
        """
        try:
            # Calculate statistics
            type_counts = {}
            confidence_sum = 0
            
            for sugg in suggestions:
                type_counts[sugg['type']] = type_counts.get(sugg['type'], 0) + 1
                confidence_sum += sugg['confidence']
            
            avg_confidence = confidence_sum / len(suggestions) if suggestions else 0
            
            # Generate report
            report = f"""
REDACTION REPORT
===============
Generated: {datetime.now().isoformat()}

File Information:
---------------
Original File: {os.path.basename(original_file)}
Redacted File: {os.path.basename(redacted_file)}
File Size: {os.path.getsize(original_file) / 1024:.2f} KB

Redaction Summary:
----------------
Total Redactions: {len(suggestions)}
Average Confidence: {avg_confidence:.2f}%

Redaction Types:
--------------
{self._format_type_counts(type_counts)}

Detailed Redactions:
-----------------
{self._format_redactions(suggestions)}

Security Note:
------------
This report contains hashed versions of sensitive data for audit purposes.
"""
            return report
        
        except Exception as e:
            raise RuntimeError(f"Report generation failed: {e}")

    def _format_type_counts(self, type_counts: Dict[str, int]) -> str:
        return '\n'.join(f"- {type_}: {count} instances" 
                        for type_, count in type_counts.items())

    def _format_redactions(self, suggestions: List[Dict]) -> str:
        return '\n'.join(
            f"#{i+1}:\n"
            f"  Type: {s['type']}\n"
            f"  Confidence: {s['confidence']}%\n"
            f"  Reason: {s.get('reason', 'N/A')}\n"
            for i, s in enumerate(suggestions)
        )