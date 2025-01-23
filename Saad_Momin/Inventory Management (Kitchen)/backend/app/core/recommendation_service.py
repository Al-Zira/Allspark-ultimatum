from typing import List, Dict, Optional
from app.models.inventory import InventoryItem
from app.ai.gemini_service import GeminiService
from datetime import datetime, timedelta
from app.core.logger import logger
from sqlalchemy.orm import Session

class RecommendationService:
    def __init__(self, db: Session):
        self.db = db
        self.gemini_service = GeminiService()
        self._context = []

    async def get_recommendations(self, user_preferences: Optional[Dict] = None) -> Dict:
        """Get meal and shopping recommendations based on current inventory"""
        try:
            # Get current inventory and create a lookup dictionary
            inventory = self.db.query(InventoryItem).all()
            inventory_dict = {
                item.name.lower(): {
                    'quantity': item.quantity,
                    'unit': item.unit
                } for item in inventory
            }
            inventory_items = [
                f"{item.name} ({item.quantity} {item.unit})"
                for item in inventory
            ]

            if not inventory_items:
                return {
                    "meal_recommendations": [],
                    "shopping_recommendations": ["Your inventory is empty. Consider adding some basic items."]
                }

            # Build context from previous interactions
            context = "\n".join(self._context[-5:])  # Keep last 5 interactions
            
            # Build preference string
            preferences = ""
            if user_preferences:
                preferences = "Consider these preferences:\n"
                if "dietary" in user_preferences:
                    preferences += f"- Dietary restrictions: {user_preferences['dietary']}\n"
                if "cuisine" in user_preferences:
                    preferences += f"- Preferred cuisine: {user_preferences['cuisine']}\n"
                if "difficulty" in user_preferences:
                    preferences += f"- Cooking difficulty: {user_preferences['difficulty']}\n"
                if "time" in user_preferences:
                    preferences += f"- Available cooking time: {user_preferences['time']} minutes\n"

            # Generate meal recommendations using AI
            meal_prompt = f"""
            You are a meal planning AI assistant. I have these ingredients in my kitchen:
            {', '.join(inventory_items)}

            {preferences}

            Please suggest 3 simple meals I can make, considering these requirements:
            1. Use ingredients I have when possible
            2. Keep cooking time under {user_preferences.get('time', 30)} minutes
            3. Keep difficulty level to {user_preferences.get('difficulty', 'medium')}
            4. Focus on {user_preferences.get('cuisine', 'any')} cuisine if specified
            5. Follow dietary restrictions: {user_preferences.get('dietary', 'none')}

            For each meal, you MUST:
            1. Check each ingredient against my inventory
            2. List ALL required ingredients, including common items like oil, salt, spices, etc.
            3. Clearly separate ingredients into:
               - available_ingredients (what I have in inventory)
               - missing_ingredients (what I need to buy, including common cooking items)
            4. For missing ingredients, specify exact quantities needed

            Format your response as a JSON object with this structure:
            {{
                "meals": [
                    {{
                        "name": "Simple meal name",
                        "cuisine": "Type of cuisine",
                        "difficulty": "easy",
                        "time_minutes": 30,
                        "available_ingredients": [
                            "ingredient 1 (2 kg from inventory)",
                            "ingredient 2 (500g from inventory)"
                        ],
                        "missing_ingredients": [
                            "vegetable oil (200ml for cooking)",
                            "salt (2 tsp)",
                            "black pepper (1 tsp)",
                            "garlic (3 cloves)",
                            "mixed vegetables (500g)"
                        ],
                        "instructions": ["First step", "Second step"],
                        "nutritional_info": {{
                            "calories": "400 kcal",
                            "protein": "15g",
                            "carbs": "45g",
                            "fat": "12g"
                        }}
                    }}
                ],
                "shopping_list": [
                    "vegetable oil (500ml total needed)",
                    "salt (5 tsp total needed)",
                    "black pepper (3 tsp total needed)",
                    "garlic (8 cloves)",
                    "mixed vegetables (1.2 kg total)"
                ],
                "storage_tips": [
                    "Store fresh vegetables in the crisper drawer",
                    "Keep spices in airtight containers"
                ],
                "meal_prep_suggestions": [
                    "Chop vegetables in advance",
                    "Measure spices before starting"
                ]
            }}
            
            IMPORTANT RULES:
            1. Include ALL necessary ingredients, even common ones like oil, salt, spices
            2. The shopping_list must include everything not in my inventory
            3. Consolidate quantities if the same ingredient is needed for multiple meals
            4. Be specific about quantities needed for each ingredient
            5. Check ingredient names exactly as they appear in my inventory
            6. For the Fish and Chips recipe, include all batter ingredients
            7. For stir-fry recipes, include sauce ingredients
            8. For recipes with vegetables, specify which vegetables and quantities
            """

            logger.info(f"Generating recommendations with preferences: {preferences}")
            meal_response = await self.gemini_service.generate_json_content(meal_prompt)
            
            if not meal_response:
                logger.error("No response received from AI service")
                return {
                    "meal_recommendations": [],
                    "shopping_recommendations": ["Unable to generate recommendations at this time"],
                    "storage_tips": [],
                    "meal_prep_suggestions": []
                }
            
            logger.info(f"Received AI response: {meal_response}")
            
            # Process meal recommendations
            meal_recommendations = []
            shopping_dict = {}  # Use dict to track quantities
            storage_tips = []
            meal_prep_suggestions = []
            
            try:
                if isinstance(meal_response, dict) and "meals" in meal_response:
                    for meal in meal_response["meals"]:
                        try:
                            recommendation = {
                                "name": str(meal.get("name", "Unnamed Meal")),
                                "cuisine": str(meal.get("cuisine", "Not specified")),
                                "difficulty": str(meal.get("difficulty", "medium")),
                                "time_minutes": int(meal.get("time_minutes", 30)),
                                "instructions": [str(step) for step in meal.get("instructions", [])],
                                "nutritional_info": {
                                    k: str(v) for k, v in meal.get("nutritional_info", {}).items()
                                }
                            }
                            
                            # Process ingredients
                            if "available_ingredients" in meal:
                                recommendation["available_ingredients"] = [
                                    str(ing) for ing in meal.get("available_ingredients", [])
                                ]
                            if "missing_ingredients" in meal:
                                missing = meal.get("missing_ingredients", [])
                                recommendation["missing_ingredients"] = [str(ing) for ing in missing]
                                
                                # Extract ingredients and quantities for shopping list
                                for item in missing:
                                    item = str(item)
                                    # Try to extract quantity from the item string
                                    if '(' in item and ')' in item:
                                        base_item = item.split('(')[0].strip().lower()
                                        quantity = item.split('(')[1].split(')')[0]
                                        if base_item not in shopping_dict:
                                            shopping_dict[base_item] = quantity
                                    else:
                                        if item.lower() not in shopping_dict:
                                            shopping_dict[item.lower()] = "quantity not specified"
                                
                            meal_recommendations.append(recommendation)
                            
                        except Exception as e:
                            logger.error(f"Error processing meal: {str(e)}")
                            continue
                
                # Get storage tips and meal prep suggestions
                if isinstance(meal_response.get("storage_tips"), list):
                    storage_tips = [str(tip) for tip in meal_response["storage_tips"]]
                
                if isinstance(meal_response.get("meal_prep_suggestions"), list):
                    meal_prep_suggestions = [str(suggestion) for suggestion in meal_response["meal_prep_suggestions"]]
                
                # Create final shopping list with quantities
                shopping_list = [
                    f"{item} ({quantity})" for item, quantity in shopping_dict.items()
                ] if shopping_dict else ["No additional ingredients needed"]
                
                # Update context with successful meals
                if meal_recommendations:
                    self._context.append(f"Generated meals: {[meal['name'] for meal in meal_recommendations]}")
            
            except Exception as e:
                logger.error(f"Error processing AI response: {str(e)}")
                shopping_list = ["Error processing shopping list"]
            
            result = {
                "meal_recommendations": meal_recommendations,
                "shopping_recommendations": sorted(shopping_list),
                "storage_tips": storage_tips if storage_tips else ["No storage tips available"],
                "meal_prep_suggestions": meal_prep_suggestions if meal_prep_suggestions else ["No meal prep suggestions available"]
            }
            
            logger.info(f"Returning recommendations: {len(meal_recommendations)} meals, {len(shopping_list)} shopping items")
            return result

        except Exception as e:
            logger.error(f"Error in get_recommendations: {str(e)}")
            return {
                "meal_recommendations": [],
                "shopping_recommendations": ["Error generating recommendations. Please try again."],
                "storage_tips": [],
                "meal_prep_suggestions": []
            }

    def clear_context(self):
        """Clear the recommendation context"""
        self._context = []