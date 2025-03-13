import google.generativeai as genai
from typing import Optional, Dict, Any, Union
import os
import json
import re
from app.core.logger import logger

class GeminiService:
    def __init__(self):
        """Initialize the Gemini service with API key and model configuration"""
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable not set")
            
            # Configure the Gemini API
            genai.configure(api_key=api_key)
            
            # Initialize the model for async operations
            self.model = genai.GenerativeModel('gemini-1.5-flash')  # Using gemini-pro for better text generation
            
            # Create a wrapper for backward compatibility
            self.chat_model = self._create_chat_model_wrapper()
            
            # Set default parameters for balanced JSON generation
            self.temperature = 0.7  # Higher temperature for more creative recommendations
            self.top_p = 0.9
            self.top_k = 40
            
            logger.info("GeminiService initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing GeminiService: {str(e)}")
            raise
    
    def _create_chat_model_wrapper(self):
        """Create a wrapper for backward compatibility with chat_model attribute"""
        class ChatModelWrapper:
            def __init__(self, parent):
                self.parent = parent
            
            def generate_content(self, prompt, **kwargs):
                # Use the parent's model but with JSON cleaning
                response = self.parent.model.generate_content(prompt, **kwargs)
                if not response or not response.text:
                    return response
                
                # Create a new response object with cleaned text for JSON prompts
                if '"' in prompt or '{' in prompt or '[' in prompt:
                    cleaned_text = self.parent._clean_json_text(response.text)
                    validated_text = self.parent._validate_json_structure(cleaned_text)
                    # Create a new response-like object
                    class CleanedResponse:
                        def __init__(self, text):
                            self.text = text
                    return CleanedResponse(validated_text)
                return response
        
        return ChatModelWrapper(self)
    
    def configure_model(self, temperature: float = 0.1, top_p: float = 0.95, top_k: int = 40):
        """Configure model parameters"""
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
    
    def _clean_json_text(self, text: str) -> str:
        """Clean and format JSON text to ensure valid structure"""
        try:
            # Remove any non-JSON content before the first { and after the last }
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                text = text[json_start:json_end]
            
            # Remove trailing commas inside arrays and objects
            text = re.sub(r',(\s*[}\]])', r'\1', text)
            
            # Try to parse and re-serialize to ensure valid JSON
            try:
                parsed = json.loads(text)
                # Ensure meal plan structure is complete
                if "meal_plan" in parsed and "days" in parsed["meal_plan"]:
                    for day in parsed["meal_plan"]["days"]:
                        if "meals" in day:
                            for meal in day["meals"]:
                                # Ensure missing_ingredients is a list
                                if "missing_ingredients" not in meal:
                                    meal["missing_ingredients"] = []
                                elif not isinstance(meal["missing_ingredients"], list):
                                    meal["missing_ingredients"] = []
                                # Ensure inventory_match is a number
                                if "inventory_match" not in meal:
                                    meal["inventory_match"] = 100
                                elif not isinstance(meal["inventory_match"], (int, float)):
                                    meal["inventory_match"] = 100
                return json.dumps(parsed, separators=(',', ':'))
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                logger.error(f"Failed JSON text: {text}")
                return text
            
        except Exception as e:
            logger.error(f"Error cleaning JSON text: {str(e)}")
            return text
    
    def _fix_truncated_meal_plan(self, text: str) -> str:
        """Fix a truncated meal plan by completing the structure"""
        try:
            # First try to parse the JSON
            try:
                json_data = json.loads(text)
                if "meal_plan" in json_data and "days" in json_data["meal_plan"]:
                    return text
            except json.JSONDecodeError:
                pass
            
            # Find all complete days
            complete_days = []
            day_starts = [m.start() for m in re.finditer(r'"day":\s*\d+', text)]
            
            for i, start in enumerate(day_starts):
                try:
                    # Find the start of the next day or end of text
                    next_start = day_starts[i + 1] if i + 1 < len(day_starts) else len(text)
                    day_text = text[start:next_start]
                    
                    # Check if this day has complete meals
                    meal_count = len(re.findall(r'"type":\s*"(?:breakfast|lunch|dinner)"', day_text))
                    if meal_count != 3:
                        continue
                    
                    # Check for complete ingredients sections
                    ingredients_starts = [m.start() for m in re.finditer(r'"ingredients":\s*\[', day_text)]
                    if len(ingredients_starts) != 3:
                        continue
                    
                    # Ensure each ingredients section is complete
                    is_complete = True
                    for ing_start in ingredients_starts:
                        # Find the matching closing bracket
                        bracket_count = 1
                        for j, char in enumerate(day_text[ing_start + len('"ingredients": ['):], ing_start + len('"ingredients": [')):
                            if char == '[':
                                bracket_count += 1
                            elif char == ']':
                                bracket_count -= 1
                                if bracket_count == 0:
                                    break
                        if bracket_count != 0:
                            is_complete = False
                            break
                    
                    if not is_complete:
                        continue
                    
                    # Try to parse this day's JSON by completing the structure
                    day_json = '{' + day_text.rstrip(',') + '}'
                    try:
                        day_data = json.loads(day_json)
                        if self._validate_day_structure(day_data):
                            complete_days.append(day_data)
                    except json.JSONDecodeError:
                        continue
                except Exception as e:
                    logger.error(f"Error processing day: {str(e)}")
                    continue
            
            if not complete_days:
                return text
            
            # Sort days by day number
            complete_days.sort(key=lambda x: x["day"])
            
            # Create a valid meal plan with complete days
            result = {
                "meal_plan": {
                    "days": complete_days
                }
            }
            
            # Validate the final structure
            try:
                return json.dumps(result)
            except Exception as e:
                logger.error(f"Error creating final JSON: {str(e)}")
                return text
            
        except Exception as e:
            logger.error(f"Error fixing truncated meal plan: {str(e)}")
            return text
    
    def _validate_day_structure(self, day_data: Dict) -> bool:
        """Validate the structure of a single day in the meal plan"""
        try:
            if not isinstance(day_data, dict) or "day" not in day_data or "meals" not in day_data:
                return False
            
            if not isinstance(day_data["meals"], list) or len(day_data["meals"]) != 3:
                return False
            
            meal_types = set()
            for meal in day_data["meals"]:
                if not isinstance(meal, dict):
                    return False
                    
                required_fields = ["type", "name", "ingredients", "inventory_match", "missing_ingredients"]
                if not all(field in meal for field in required_fields):
                    return False
                
                # Check meal type
                if meal["type"] not in ["breakfast", "lunch", "dinner"]:
                    return False
                meal_types.add(meal["type"])
                
                # Validate ingredients
                if not isinstance(meal["ingredients"], list):
                    return False
                
                for ingredient in meal["ingredients"]:
                    if not isinstance(ingredient, dict):
                        return False
                    if not all(field in ingredient for field in ["name", "quantity", "unit"]):
                        return False
                    if not all(isinstance(ingredient[field], str) for field in ["name", "quantity", "unit"]):
                        return False
                
                # Validate inventory match
                if not isinstance(meal["inventory_match"], (int, float)):
                    try:
                        meal["inventory_match"] = float(meal["inventory_match"])
                    except (ValueError, TypeError):
                        return False
                
                # Validate missing ingredients
                if not isinstance(meal["missing_ingredients"], list):
                    return False
                if not all(isinstance(item, str) for item in meal["missing_ingredients"]):
                    return False
            
            # Ensure we have all meal types
            if len(meal_types) != 3 or not meal_types == {"breakfast", "lunch", "dinner"}:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating day structure: {str(e)}")
            return False
    
    def _validate_json_structure(self, text: str) -> str:
        """Validate and fix JSON structure"""
        try:
            # First try to parse as is
            try:
                json.loads(text)
                return text
            except json.JSONDecodeError:
                pass
            
            # If this is a meal plan, handle meal plan validation
            if '"meal_plan"' in text and '"days"' in text:
                # Find all complete days
                day_matches = list(re.finditer(r'{\s*"day":\s*(\d+)', text))
                complete_days = []
                
                for i, day_match in enumerate(day_matches):
                    try:
                        day_start = day_match.start()
                        # Find the end of this day's data
                        next_day_start = day_matches[i + 1].start() if i + 1 < len(day_matches) else len(text)
                        day_text = text[day_start:next_day_start]
                        
                        # Check if this day has all required components
                        if not all(key in day_text for key in ['"meals":', '"type":', '"name":', '"ingredients":', '"inventory_match":', '"missing_ingredients":']):
                            continue
                        
                        # Check for complete meal structure
                        meal_types = re.findall(r'"type":\s*"(breakfast|lunch|dinner)"', day_text)
                        if len(meal_types) != 3 or len(set(meal_types)) != 3:
                            continue
                        
                        # Ensure all ingredients sections are complete
                        ingredients_sections = re.findall(r'"ingredients":\s*\[(.*?)\]', day_text, re.DOTALL)
                        if len(ingredients_sections) != 3:
                            continue
                        
                        # Verify each ingredients section has complete items
                        valid_ingredients = True
                        for ingredients in ingredients_sections:
                            if not all(key in ingredients for key in ['"name"', '"quantity"', '"unit"']):
                                valid_ingredients = False
                                break
                        
                        if not valid_ingredients:
                            continue
                        
                        # This appears to be a complete day
                        complete_days.append(day_text.rstrip(','))
                    except Exception as e:
                        logger.error(f"Error processing day: {str(e)}")
                        continue
                
                if complete_days:
                    # Create a valid meal plan structure
                    result = {
                        "meal_plan": {
                            "days": []
                        }
                    }
                    
                    # Parse and add each complete day
                    for day_text in complete_days:
                        try:
                            day_json = '{' + day_text + '}'
                            day_data = json.loads(day_json)
                            result["meal_plan"]["days"].append(day_data)
                        except json.JSONDecodeError:
                            continue
                    
                    # Sort days by day number
                    result["meal_plan"]["days"].sort(key=lambda x: x["day"])
                    
                    # Return the validated JSON
                    return json.dumps(result, separators=(',', ':'))
            
            return text
            
        except Exception as e:
            logger.error(f"Error validating JSON structure: {str(e)}")
            return text
    
    async def generate_json_content(self, prompt: str) -> Optional[Dict[str, Any]]:
        """Generate JSON content from a prompt"""
        try:
            # Configure model for JSON generation
            self.configure_model(temperature=0.7, top_p=0.9, top_k=40)
            
            # Add JSON formatting reminder to the prompt
            json_prompt = f"""
            {prompt}
            
            IMPORTANT: Your response must be valid JSON. Do not include any text before or after the JSON.
            Focus on providing a complete and valid JSON structure.
            """
            
            # Generate content
            response = await self.generate_content(json_prompt)
            if not response:
                logger.error("No response received from Gemini")
                return None
            
            # Clean and parse JSON
            try:
                # Extract JSON from the response
                json_match = re.search(r'\{[\s\S]*\}', response)
                if not json_match:
                    logger.error("No JSON object found in response")
                    return None
                
                json_str = json_match.group(0)
                # Clean up common JSON formatting issues
                json_str = json_str.replace('\n', ' ')
                json_str = re.sub(r'(?<!\\)"(\w+)":', r'"\1":', json_str)  # Fix unquoted keys
                json_str = re.sub(r'(\w+):', r'"\1":', json_str)  # Quote unquoted keys
                json_str = re.sub(r',\s*}', '}', json_str)  # Remove trailing commas
                json_str = re.sub(r',\s*]', ']', json_str)  # Remove trailing commas in arrays
                
                # Parse JSON
                data = json.loads(json_str)
                
                # Validate structure
                if not isinstance(data, dict):
                    logger.error("Response is not a JSON object")
                    return None
                
                if "meals" not in data or not isinstance(data["meals"], list):
                    logger.error("Response missing required 'meals' array")
                    return None
                
                # Ensure all required fields are present and properly formatted
                for meal in data["meals"]:
                    meal["name"] = str(meal.get("name", "Unnamed Meal"))
                    meal["cuisine"] = str(meal.get("cuisine", "Not specified"))
                    meal["difficulty"] = str(meal.get("difficulty", "medium"))
                    meal["time_minutes"] = int(meal.get("time_minutes", 30))
                    meal["instructions"] = [str(step) for step in meal.get("instructions", [])]
                    meal["ingredients_needed"] = [str(ing) for ing in meal.get("ingredients_needed", [])]
                    meal["nutritional_info"] = {
                        k: str(v) for k, v in meal.get("nutritional_info", {}).items()
                    }
                
                # Ensure other lists are properly formatted
                data["shopping_list"] = [str(item) for item in data.get("shopping_list", [])]
                data["storage_tips"] = [str(tip) for tip in data.get("storage_tips", [])]
                data["meal_prep_suggestions"] = [str(sugg) for sugg in data.get("meal_prep_suggestions", [])]
                
                logger.info("Successfully generated and validated JSON response")
                return data
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing error: {str(e)}")
                return None
            except Exception as e:
                logger.error(f"Error processing JSON response: {str(e)}")
                return None
            
        except Exception as e:
            logger.error(f"Error in generate_json_content: {str(e)}")
            return None
    
    async def generate_content(self, prompt: str) -> Optional[str]:
        """Generate text content using the Gemini model"""
        try:
            # Create a generation config
            generation_config = {
                'temperature': self.temperature,
                'top_p': self.top_p,
                'top_k': self.top_k
            }
            
            # Generate content (synchronously)
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            if not response or not response.text:
                logger.error("Empty response from Gemini model")
                return None
            
            # For JSON-like prompts, clean the response
            if '"' in prompt or '{' in prompt or '[' in prompt:
                cleaned_text = self._clean_json_text(response.text)
                return self._validate_json_structure(cleaned_text)
            
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            return None
    
    async def get_market_price(self, item_name: str, category: Optional[str] = None) -> Optional[float]:
        """Get current market price for an item using Gemini AI"""
        try:
            # Default prices by category
            default_prices = {
                "meat": 12.99,
                "dairy": 4.99,
                "produce": 3.99,
                "grains": 2.99,
                "beverages": 3.99,
                "spices": 5.99,
                "snacks": 4.99,
                "condiments": 3.99,
                "canned": 2.99,
                "frozen": 5.99,
                "baking": 3.99,
                "other": 4.99
            }

            # If it's a default category request, return the default price
            if item_name.startswith("default_") or item_name.startswith("average_"):
                category_key = category.lower() if category else "other"
                return default_prices.get(category_key, 4.99)

            # Construct the prompt
            prompt = f"""
            What is the current average market price (in USD) for {item_name}
            {f'in the {category} category' if category else ''}?
            Consider standard retail prices and provide a reasonable estimate.
            Please respond with ONLY a number representing the price per kg/liter/unit.
            For example: 12.99
            """

            # Configure model for precise numerical output
            self.configure_model(temperature=0.1, top_p=0.95, top_k=40)
            
            # Get response from Gemini
            response = await self.generate_content(prompt)
            if not response:
                # Fallback to category default
                if category and category.lower() in default_prices:
                    return default_prices[category.lower()]
                return default_prices["other"]
            
            # Extract the price from the response
            try:
                # Clean the response and extract the first number
                price_match = re.search(r'\d+\.?\d*', response)
                if price_match:
                    price = float(price_match.group())
                    # Validate the price is reasonable (between $0.10 and $1000)
                    if 0.10 <= price <= 1000.0:
                        return price
                
                # If price is invalid, use category default
                if category and category.lower() in default_prices:
                    return default_prices[category.lower()]
                return default_prices["other"]
                
            except ValueError:
                logger.error(f"Failed to parse price from response: {response}")
                # Fallback to category default
                if category and category.lower() in default_prices:
                    return default_prices[category.lower()]
                return default_prices["other"]
                
        except Exception as e:
            logger.error(f"Error getting market price: {str(e)}")
            # Fallback to category default
            if category and category.lower() in default_prices:
                return default_prices[category.lower()]
            return default_prices["other"]
