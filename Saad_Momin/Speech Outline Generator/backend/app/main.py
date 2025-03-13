from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel
import google.generativeai as genai
import os
from dotenv import load_dotenv
from typing import Optional
from fastapi.responses import StreamingResponse, FileResponse
import tempfile

# Load environment variables
load_dotenv()

# Initialize Gemini AI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

app = FastAPI(title="Speech Outline Generator API")

class SpeechRequest(BaseModel):
    topic: str
    language: str
    tone: str
    sections: int
    duration: int
    audience_type: str
    presentation_style: str
    purpose: str
    template: str
    word_limit: int
    formatting_style: str
    topic_details: Optional[str] = None

# Move translations to a separate dictionary
translations = {
    "French": {
        "key_points": "Points Clés",
        "potential_subtopics": "Sous-thèmes Potentiels",
        "suggested_transitions": "Transitions Suggérées",
        "closing_recommendations": "Recommandations Finales"
    },
    "Spanish": {
        "key_points": "Puntos Clave",
        "potential_subtopics": "Subtemas Potenciales",
        "suggested_transitions": "Transiciones Sugeridas",
        "closing_recommendations": "Recomendaciones Finales"
    },
    "German": {
        "key_points": "Hauptpunkte",
        "potential_subtopics": "Mögliche Unterthemen",
        "suggested_transitions": "Vorgeschlagene Übergänge",
        "closing_recommendations": "Abschließende Empfehlungen"
    },
    "Mandarin": {
        "key_points": "要点",
        "potential_subtopics": "潜在子主题",
        "suggested_transitions": "建议过渡",
        "closing_recommendations": "结束建议"
    },
    "Japanese": {
        "key_points": "主要ポイント",
        "potential_subtopics": "考えられるサブトピック",
        "suggested_transitions": "推奨される移行",
        "closing_recommendations": "最終提案"
    },
    "Korean": {
        "key_points": "주요 포인트",
        "potential_subtopics": "잠재적 하위 주제",
        "suggested_transitions": "제안된 전환",
        "closing_recommendations": "마무리 권장사항"
    },
    "Italian": {
        "key_points": "Punti Chiave",
        "potential_subtopics": "Possibili Sottotemi",
        "suggested_transitions": "Transizioni Suggerite",
        "closing_recommendations": "Raccomandazioni Finali"
    },
    "Portuguese": {
        "key_points": "Pontos-Chave",
        "potential_subtopics": "Subtópicos Potenciais",
        "suggested_transitions": "Transições Sugeridas",
        "closing_recommendations": "Recomendações Finais"
    },
    "Russian": {
        "key_points": "Ключевые Моменты",
        "potential_subtopics": "Возможные Подтемы",
        "suggested_transitions": "Предлагаемые Переходы",
        "closing_recommendations": "Заключительные Рекомендации"
    },
    "Arabic": {
        "key_points": "النقاط الرئيسية",
        "potential_subtopics": "المواضيع الفرعية المحتملة",
        "suggested_transitions": "الانتقالات المقترحة",
        "closing_recommendations": "التوصيات الختامية"
    },
    "Hindi": {
        "key_points": "मुख्य बिंदु",
        "potential_subtopics": "संभावित उप-विषय",
        "suggested_transitions": "सुझाए गए संक्रमण",
        "closing_recommendations": "समापन सिफारिशें"
    },
    "Turkish": {
        "key_points": "Ana Noktalar",
        "potential_subtopics": "Olası Alt Konular",
        "suggested_transitions": "Önerilen Geçişler",
        "closing_recommendations": "Kapanış Önerileri"
    },
    "English": {
        "key_points": "Key Points",
        "potential_subtopics": "Potential Subtopics",
        "suggested_transitions": "Suggested Transitions",
        "closing_recommendations": "Closing Recommendations"
    }
}

@app.post("/generate-outline")
async def generate_outline(request: SpeechRequest):
    try:
        # Get translations for the selected language
        lang_trans = translations.get(request.language, translations["English"])
        
        prompt = f"""Create a speech outline with the following specifications:
        - Topic: {request.topic}
        - Strict Language: {request.language} (Please ensure ALL text, including section headers and structural elements, is in {request.language})
        - Tone: {request.tone}
        - Number of Sections: {request.sections}
        - Speech Duration: {request.duration} minutes
        - Target Audience: {request.audience_type}
        - Presentation Style: {request.presentation_style}
        - Purpose/Goal: {request.purpose}
        - Word Limit: {request.word_limit} words
        - Formatting Style: {request.formatting_style}
        {f'- Additional Details: {request.topic_details}' if request.topic_details else ''}
        {f'- Template Style: {request.template}' if request.template != 'Standard' else ''}

        Outline Structure:
        1. Title (in {request.language})
        2. Target Audience and Purpose Statement
        3. Time Allocation per Section
        4. For each section include:
           - {lang_trans["key_points"]}
           - {lang_trans["potential_subtopics"]}
           - {lang_trans["suggested_transitions"]}
           - Estimated Time
        5. {lang_trans["closing_recommendations"]}
        6. Visual Aid Suggestions
        7. Engagement Techniques

        Important: 
        - Ensure that ALL text, including section headers, structural elements, and content is in {request.language}
        - Keep within the {request.word_limit} word limit
        - Format according to the {request.formatting_style} style
        - Include time markers for each section to total {request.duration} minutes"""

        response = model.generate_content([
            {"role": "user", "parts": [f"You are an expert speech and content outline generator. Always respond entirely in {request.language}.\n\n{prompt}"]}
        ])
        
        return {
            "outline": response.text,
            "word_count": len(response.text.split()),
            "duration": request.duration,
            "sections": request.sections
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/download-outline")
async def download_outline(request: SpeechRequest):
    try:
        # Get translations for the selected language
        lang_trans = translations.get(request.language, translations["English"])
        
        # Reuse the same prompt generation logic
        prompt = f"""Create a speech outline with the following specifications:
        - Topic: {request.topic}
        - Strict Language: {request.language} (Please ensure ALL text, including section headers and structural elements, is in {request.language})
        - Tone: {request.tone}
        - Number of Sections: {request.sections}
        - Speech Duration: {request.duration} minutes
        - Target Audience: {request.audience_type}
        - Presentation Style: {request.presentation_style}
        - Purpose/Goal: {request.purpose}
        - Word Limit: {request.word_limit} words
        - Formatting Style: {request.formatting_style}
        {f'- Additional Details: {request.topic_details}' if request.topic_details else ''}
        {f'- Template Style: {request.template}' if request.template != 'Standard' else ''}

        Outline Structure:
        1. Title (in {request.language})
        2. Target Audience and Purpose Statement
        3. Time Allocation per Section
        4. For each section include:
           - {lang_trans["key_points"]}
           - {lang_trans["potential_subtopics"]}
           - {lang_trans["suggested_transitions"]}
           - Estimated Time
        5. {lang_trans["closing_recommendations"]}
        6. Visual Aid Suggestions
        7. Engagement Techniques

        Important: 
        - Ensure that ALL text, including section headers, structural elements, and content is in {request.language}
        - Keep within the {request.word_limit} word limit
        - Format according to the {request.formatting_style} style
        - Include time markers for each section to total {request.duration} minutes"""

        response = model.generate_content([
            {"role": "user", "parts": [f"You are an expert speech and content outline generator. Always respond entirely in {request.language}.\n\n{prompt}"]}
        ])
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            tmp.write(response.text)
            tmp_path = tmp.name

        filename = f"speech_outline_{request.topic.lower().replace(' ', '_')}.txt"
        
        # Return the file as a downloadable response
        return FileResponse(
            tmp_path,
            media_type='text/plain',
            filename=filename,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 