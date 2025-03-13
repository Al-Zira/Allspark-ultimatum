import os
import json
import asyncio
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
import warnings
warnings.filterwarnings('ignore')

class LanguageLearningAssistant:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")

        # Initialize Gemini LLM
        self.llm = GoogleGenerativeAI(
            model='gemini-pro',
            temperature=0.7,
            google_api_key=api_key
        )
        
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
        
        # Initialize prompt templates with explicit JSON structure
        self.exercise_prompt = PromptTemplate(
            input_variables=["exercise_type", "topic", "proficiency", "target_language"],
            template="""You are a language learning assistant. Create a {exercise_type} exercise in {target_language} for a {proficiency} level student.
            Topic: {topic}

            Respond ONLY with a valid JSON object that strictly follows this format:
            {{
                "instructions": "Clear instructions in English",
                "content": "The exercise content in {target_language}",
                "correct_answers": ["answer1", "answer2"],
                "hints": "Helpful context or hints",
                "cultural_notes": "Any relevant cultural information",
                "difficulty": "{proficiency}",
                "exercise_type": "{exercise_type}",
                "topic": "{topic}",
                "target_language": "{target_language}"
            }}
            """
        )
        
        self.evaluation_prompt = PromptTemplate(
            input_variables=["exercise_type", "user_response", "correct_answer", "target_language", "proficiency"],
            template="""Evaluate this {target_language} response for a {proficiency} level student.

            User's response: {user_response}
            Correct answer: 
            {correct_answer}

            Respond ONLY with a valid JSON object that strictly follows this format:
            {{
                "accuracy_score": 0.85,
                "grammar_feedback": "Specific grammar feedback",
                "vocabulary_feedback": "Vocabulary usage analysis",
                "natural_flow_feedback": "Analysis of natural flow",
                "improvement_suggestions": ["suggestion1", "suggestion2"],
                "positive_points": ["positive1", "positive2"]
            }}
            """
        )
        
        self.translation_prompt = PromptTemplate(
            input_variables=["source_text", "source_language", "target_language"],
            template="""Translate the following text from {source_language} to {target_language}.

            Source text: {source_text}

            Respond ONLY with a valid JSON object that strictly follows this format:
            {{
                "translation": "translated text",
                "pronunciation": "pronunciation guide if applicable",
                "alternate_translations": ["alternative1", "alternative2"],
                "notes": "any relevant cultural or contextual notes",
                "formal_level": "formal/informal classification of the translation"
            }}
            """
        )

    async def generate_exercise(self, target_language: str, proficiency: str, 
                         exercise_type: str, topic: str) -> dict:
        """Generate a language exercise using Gemini LLM with streaming"""
        try:
            chain = LLMChain(
                llm=self.llm,
                prompt=self.exercise_prompt
            )
            
            formatted_prompt = self.exercise_prompt.format(
                exercise_type=exercise_type,
                topic=topic,
                proficiency=proficiency,
                target_language=target_language
            )
            
            response_chunks = []
            async for chunk in self.llm.astream(formatted_prompt):
                print(chunk, end="", flush=True)
                response_chunks.append(chunk)
            
            response = ''.join(response_chunks)
            expected_keys = [
                "instructions",
                "content",
                "correct_answers",
                "hints",
                "cultural_notes",
                "difficulty",
                "exercise_type",
                "topic",
                "target_language"
            ]
            
            exercise = self.parse_llm_response(response, expected_keys)
            # Ensure correct_answers is a list
            if not isinstance(exercise.get("correct_answers", []), list):
                exercise["correct_answers"] = []
            return exercise
            
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
                "topic": topic,
                "target_language": target_language
            }

    async def evaluate_response(self, exercise_type: str, user_response: str, correct_answer: list, target_language: str, proficiency: str) -> dict:
        """Evaluate user's response using Gemini LLM with streaming"""
        try:
            chain = LLMChain(
                llm=self.llm,
                prompt=self.evaluation_prompt
            )
            
            # Format correct answers as a bulleted list
            correct_answer_str = "\n".join([f"- {ans}" for ans in correct_answer])
            
            formatted_prompt = self.evaluation_prompt.format(
                exercise_type=exercise_type,
                user_response=user_response,
                correct_answer=correct_answer_str,
                target_language=target_language,
                proficiency=proficiency
            )
            
            response_chunks = []
            async for chunk in self.llm.astream(formatted_prompt):
                print(chunk, end="", flush=True)
                response_chunks.append(chunk)
            
            response = ''.join(response_chunks)
            expected_keys = [
                "accuracy_score",
                "grammar_feedback",
                "vocabulary_feedback",
                "natural_flow_feedback",
                "improvement_suggestions",
                "positive_points"
            ]
            
            return self.parse_llm_response(response, expected_keys)
            
        except Exception as e:
            return {
                "error": str(e),
                "accuracy_score": 0.0,
                "grammar_feedback": "Error evaluating response",
                "vocabulary_feedback": "",
                "natural_flow_feedback": "",
                "improvement_suggestions": [],
                "positive_points": []
            }

    async def translate_text(self, source_text: str, source_language: str, target_language: str) -> dict:
        """Translate text using Gemini LLM with streaming"""
        try:
            chain = LLMChain(
                llm=self.llm,
                prompt=self.translation_prompt
            )
            
            formatted_prompt = self.translation_prompt.format(
                source_text=source_text,
                source_language=source_language,
                target_language=target_language
            )
            
            response_chunks = []
            async for chunk in self.llm.astream(formatted_prompt):
                print(chunk, end="", flush=True)
                response_chunks.append(chunk)
            
            response = ''.join(response_chunks)
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
                "translation": "Translation failed",
                "pronunciation": "",
                "alternate_translations": [],
                "notes": "Error occurred during translation",
                "formal_level": ""
            }

    def parse_llm_response(self, response: str, expected_keys: list[str]) -> dict:
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

def display_exercise(exercise: dict):
    """Display the exercise in a user-friendly format"""
    print("\n--- Exercise ---")
    print(f"Type: {exercise['exercise_type']}")
    print(f"Topic: {exercise['topic']}")
    print(f"Difficulty: {exercise['difficulty']}")
    print(f"\nInstructions: {exercise['instructions']}")
    print(f"\nContent: {exercise['content']}")
    print(f"\nHints: {exercise['hints']}")
    print(f"\nCultural Notes: {exercise['cultural_notes']}")
    print("\n--- End of Exercise ---\n")

def show_correct_answers(exercise: dict):
    """Display the correct answers for the exercise."""
    print("\n--- Correct Answers ---")
    if "correct_answers" in exercise and isinstance(exercise["correct_answers"], list):
        for idx, answer in enumerate(exercise["correct_answers"], 1):
            print(f"{idx}. {answer}")
    else:
        print("No correct answers available.")
    print("--- End of Correct Answers ---\n")

def display_translation(translation: dict):
    """Display the translation results in a user-friendly format"""
    print("\n--- Translation ---")
    print(f"Translation: {translation['translation']}")
    print(f"Pronunciation: {translation.get('pronunciation', 'N/A')}")
    print(f"Alternate Translations: {', '.join(translation.get('alternate_translations', []))}")
    print(f"Notes: {translation.get('notes', 'N/A')}")
    print(f"Formal Level: {translation.get('formal_level', 'N/A')}")
    print("--- End of Translation ---\n")

async def main():
    # Initialize the assistant
    assistant = LanguageLearningAssistant()
    
    print("Welcome to the Language Learning Assistant!")
    print("Let's set up your preferences.\n")
    
    # Get user preferences
    target_language = input(f"Choose a target language ({', '.join(assistant.available_languages)}): ")
    proficiency = input(f"Choose your proficiency level ({', '.join(assistant.proficiency_levels)}): ")
    
    while True:
        # Main menu
        print("\nWhat would you like to do?")
        print("1. Generate Exercise")
        print("2. Get Translation")
        print("3. Quit")
        choice = input("Enter your choice (1/2/3): ").strip()
        
        if choice == "1":
            # Generate and evaluate exercise
            exercise_type = input(f"\nChoose an exercise type ({', '.join(assistant.exercise_types)}): ")
            topic = input(f"Choose a topic ({', '.join(assistant.exercise_topics)}): ")
            
            print("\nGenerating exercise...")
            exercise = await assistant.generate_exercise(
                target_language=target_language,
                proficiency=proficiency,
                exercise_type=exercise_type,
                topic=topic
            )
            
            if "error" in exercise:
                print(f"Error generating exercise: {exercise['error']}")
                continue
            
            display_exercise(exercise)
            user_response = input("Enter your answer: ")
            show_correct_answers(exercise)
            
            print("\nEvaluating your response...")
            feedback = await assistant.evaluate_response(
                exercise_type=exercise['exercise_type'],
                user_response=user_response,
                correct_answer=exercise['correct_answers'],
                target_language=exercise['target_language'],
                proficiency=exercise['difficulty']
            )
            if "error" in feedback:
                print(f"Error evaluating response: {feedback['error']}")
            else:
                print("\nFeedback:")
                print(json.dumps(feedback, indent=2, ensure_ascii=False))
        
        elif choice == "2":
            # Get translation
            source_text = input("\nEnter the text to translate: ")
            source_language = input(f"Enter the source language (default is English): ") or "English"
            
            print("\nTranslating text...")
            translation = await assistant.translate_text(
                source_text=source_text,
                source_language=source_language,
                target_language=target_language
            )
            if "error" in translation:
                print(f"Error translating text: {translation['error']}")
            else:
                display_translation(translation)
        
        elif choice == "3":
            # Quit the program
            print("\nThank you for using the Language Learning Assistant. Goodbye!")
            break
        else:
            print("\nInvalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    asyncio.run(main())