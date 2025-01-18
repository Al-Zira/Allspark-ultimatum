import os
from typing import List, Dict, Optional
import json
from dotenv import load_dotenv
from groq import Groq
import gradio as gr

class LanguageLearningAssistant:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")

        # Initialize Groq client
        self.client = Groq(api_key=groq_api_key)
        self.model = "llama3-8b-8192"
        
        # Initialize session history
        self.session_history = []
        
        # Define available options as instance attributes
        self.available_languages = [
            "English", "Spanish", "French", "German", "Italian", "Portuguese", 
            "Chinese", "Japanese", "Korean", "Russian", "Arabic", "Hindi",
            "Vietnamese", "Thai", "Turkish", "Dutch"
        ]
        
        self.proficiency_levels = [
            "Beginner (A1)", "Elementary (A2)", 
            "Intermediate (B1)", "Upper Intermediate (B2)", 
            "Advanced (C1)", "Mastery (C2)"
        ]
        
        self.exercise_types = [
            "Vocabulary", "Grammar", "Conversation", "Translation",
            "Reading Comprehension", "Listening Practice", 
            "Writing Exercise", "Idioms and Expressions"
        ]
        
        self.exercise_topics = [
            "Daily Life", "Travel", "Business", "Education",
            "Food and Dining", "Hobbies", "Culture", "Technology",
            "Environment", "Health and Wellness", "Social Media",
            "Current Events", "Arts and Entertainment"
        ]

    def get_llm_response(self, prompt: str) -> str:
        """Get response from Llama model using Groq"""
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful language learning assistant that provides detailed, accurate responses in JSON format."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                stream=False
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error getting LLM response: {str(e)}")

    def parse_llm_response(self, response: str, expected_keys: List[str]) -> Dict:
        """Parse and validate LLM response"""
        try:
            response = response.strip()
            start_idx = response.find('{')
            end_idx = response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                response = response[start_idx:end_idx]

            data = json.loads(response)
            
            missing_keys = [key for key in expected_keys if key not in data]
            if missing_keys:
                raise ValueError(f"Missing required keys: {missing_keys}")
                
            return data
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {str(e)}\nResponse: {response}")

    def generate_exercise(self, target_language: str, proficiency: str, 
                         exercise_type: str, topic: str) -> Dict:
        """Generate a language exercise using Llama"""
        try:
            prompt = f"""Create a {exercise_type} exercise in {target_language} for a {proficiency} level student.
            Topic: {topic}

            Respond with a JSON object that includes:
            - instructions (in English)
            - content (in {target_language})
            - correct_answers (array)
            - hints
            - cultural_notes
            - difficulty
            - exercise_type
            - topic

            Ensure all text is properly formatted and JSON is valid."""

            response = self.get_llm_response(prompt)
            
            expected_keys = [
                "instructions",
                "content",
                "correct_answers",
                "hints",
                "cultural_notes",
                "difficulty",
                "exercise_type",
                "topic"
            ]
            
            return self.parse_llm_response(response, expected_keys)
            
        except Exception as e:
            return {
                "error": str(e),
                "instructions": "Error generating exercise",
                "content": "",
                "correct_answers": [],
                "hints": "",
                "cultural_notes": "",
                "difficulty": proficiency,
                "exercise_type": exercise_type,
                "topic": topic
            }

    def translate_text(self, source_text: str, source_language: str, target_language: str) -> Dict:
        """Translate text between any two languages"""
        try:
            prompt = f"""Translate the following text from {source_language} to {target_language}.
            
            Source text: {source_text}
            
            Respond with a JSON object that includes:
            - translation (main translation)
            - pronunciation (if applicable)
            - alternate_translations (array of alternatives)
            - notes (cultural or contextual notes)
            - formal_level (formal/informal classification)

            Ensure all text is properly formatted and JSON is valid."""

            response = self.get_llm_response(prompt)
            
            expected_keys = [
                "translation",
                "pronunciation",
                "alternate_translations",
                "notes",
                "formal_level"
            ]
            
            return self.parse_llm_response(response, expected_keys)
            
        except Exception as e:
            return {
                "error": str(e),
                "translation": "",
                "pronunciation": "",
                "alternate_translations": [],
                "notes": "Error occurred during translation",
                "formal_level": ""
            }

    def create_gradio_interface(self):
        """Create Gradio interface with all user input parameters"""
        def process_exercise(target_language, proficiency, exercise_type, topic):
            try:
                exercise = self.generate_exercise(
                    target_language, proficiency, exercise_type, topic
                )
                return json.dumps(exercise, indent=2, ensure_ascii=False)
            except Exception as e:
                return str(e)

        def process_translation(text, from_lang, to_lang):
            try:
                result = self.translate_text(text, from_lang, to_lang)
                return result
            except Exception as e:
                return {
                    "error": str(e),
                    "translation": "Translation failed",
                    "pronunciation": "",
                    "alternate_translations": [],
                    "notes": str(e),
                    "formal_level": ""
                }

        # Create Gradio interface
        with gr.Blocks() as interface:
            gr.Markdown("# Language Learning Assistant (Powered by Llama)")
            
            with gr.Tabs():
                with gr.Tab("Exercise Generator"):
                    with gr.Row():
                        target_language = gr.Dropdown(
                            choices=self.available_languages,
                            value="Spanish",
                            label="Target Language"
                        )
                        proficiency = gr.Dropdown(
                            choices=self.proficiency_levels,
                            value="Beginner (A1)",
                            label="Proficiency Level"
                        )
                    
                    with gr.Row():
                        exercise_type = gr.Dropdown(
                            choices=self.exercise_types,
                            value="Vocabulary",
                            label="Exercise Type"
                        )
                        topic = gr.Dropdown(
                            choices=self.exercise_topics,
                            value="Daily Life",
                            label="Topic"
                        )
                    
                    generate_btn = gr.Button("Generate Exercise", variant="primary")
                    exercise_output = gr.Textbox(
                        label="Generated Exercise",
                        lines=10
                    )
                    
                    generate_btn.click(
                        process_exercise,
                        inputs=[target_language, proficiency, exercise_type, topic],
                        outputs=exercise_output
                    )
                
                with gr.Tab("Translator"):
                    with gr.Row():
                        source_language = gr.Dropdown(
                            choices=["Auto-detect"] + self.available_languages,
                            value="English",
                            label="From Language"
                        )
                        target_language_trans = gr.Dropdown(
                            choices=self.available_languages,
                            value="Spanish",
                            label="To Language"
                        )
                    
                    source_text = gr.Textbox(
                        label="Enter text to translate",
                        placeholder="Type or paste your text here...",
                        lines=4
                    )
                    
                    translate_btn = gr.Button("Translate", variant="primary")
                    translation_output = gr.JSON(label="Translation Results")
                    
                    translate_btn.click(
                        process_translation,
                        inputs=[source_text, source_language, target_language_trans],
                        outputs=translation_output
                    )

                    # Add example translations
                    gr.Examples(
                        examples=[
                            ["Hello, how are you?", "English", "Spanish"],
                            ["Bonjour le monde", "French", "English"],
                            ["Guten Morgen", "German", "English"],
                            ["¿Cómo estás?", "Spanish", "English"],
                        ],
                        inputs=[source_text, source_language, target_language_trans],
                        outputs=translation_output,
                        fn=process_translation,
                        cache_examples=True
                    )

        return interface

if __name__ == "__main__":
    assistant = LanguageLearningAssistant()
    interface = assistant.create_gradio_interface()
    interface.launch()