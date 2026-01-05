"""
OpenAI GPT Integration Module

This module provides integration with OpenAI's GPT models for AI-powered 
suggestions and recommendations in the food-agent-app.
"""

import os
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod

try:
    from openai import OpenAI, APIError, RateLimitError, APIConnectionError
except ImportError:
    raise ImportError(
        "openai package is required. Install it with: pip install openai"
    )


class OpenAIConfig:
    """Configuration for OpenAI integration."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        """
        Initialize OpenAI configuration.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: GPT model to use (default: gpt-4)
            temperature: Creativity/randomness (0-1, default: 0.7)
            max_tokens: Maximum response length (default: 500)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key not provided. Set OPENAI_API_KEY environment variable."
            )
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens


class OpenAIIntegration:
    """Handles interaction with OpenAI GPT models for food suggestions and recommendations."""

    def __init__(self, config: Optional[OpenAIConfig] = None):
        """
        Initialize OpenAI integration.

        Args:
            config: OpenAIConfig instance (uses defaults if not provided)
        """
        self.config = config or OpenAIConfig()
        self.client = OpenAI(api_key=self.config.api_key)

    def _call_gpt(self, messages: List[Dict[str, str]]) -> str:
        """
        Internal method to call OpenAI GPT.

        Args:
            messages: List of message dicts with 'role' and 'content'

        Returns:
            Response text from GPT

        Raises:
            APIError: If OpenAI API call fails
        """
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=messages,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
            return response.choices[0].message.content.strip()
        except RateLimitError:
            raise APIError(
                "OpenAI API rate limit exceeded. Please try again later."
            )
        except APIConnectionError:
            raise APIError(
                "Failed to connect to OpenAI API. Check your internet connection."
            )
        except APIError as e:
            raise APIError(f"OpenAI API error: {str(e)}")

    def get_meal_suggestions(
        self,
        dietary_preferences: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        cuisine_type: Optional[str] = None,
        calories_limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get AI-powered meal suggestions based on preferences and constraints.

        Args:
            dietary_preferences: List of dietary preferences (e.g., ["vegetarian", "vegan"])
            allergies: List of allergies to avoid (e.g., ["peanuts", "shellfish"])
            cuisine_type: Preferred cuisine type (e.g., "Italian", "Asian")
            calories_limit: Maximum calorie count per meal

        Returns:
            Dict containing suggestions with meals, recipes, and nutritional info
        """
        constraints = []
        if dietary_preferences:
            constraints.append(f"Dietary preferences: {', '.join(dietary_preferences)}")
        if allergies:
            constraints.append(f"Allergies to avoid: {', '.join(allergies)}")
        if cuisine_type:
            constraints.append(f"Preferred cuisine: {cuisine_type}")
        if calories_limit:
            constraints.append(f"Maximum calories: {calories_limit}")

        constraints_text = (
            "\n".join(constraints) if constraints else "No specific constraints"
        )

        prompt = f"""You are a professional nutritionist and chef. Based on the following constraints, 
provide 3 creative meal suggestions with recipes.

Constraints:
{constraints_text}

For each suggestion, provide:
1. Meal name
2. Brief description
3. Key ingredients
4. Estimated calories
5. Preparation time
6. Quick recipe steps (3-5 steps)

Format the response as a numbered list with clear sections."""

        messages = [
            {
                "role": "system",
                "content": "You are a helpful culinary AI assistant specializing in nutrition and meal planning.",
            },
            {"role": "user", "content": prompt},
        ]

        response_text = self._call_gpt(messages)

        return {
            "status": "success",
            "suggestions": response_text,
            "parameters": {
                "dietary_preferences": dietary_preferences,
                "allergies": allergies,
                "cuisine_type": cuisine_type,
                "calories_limit": calories_limit,
            },
        }

    def get_recipe_enhancement(
        self, recipe: str, enhancement_type: str = "nutritional"
    ) -> Dict[str, Any]:
        """
        Get AI suggestions to enhance or modify a recipe.

        Args:
            recipe: The recipe text to enhance
            enhancement_type: Type of enhancement - "nutritional", "simplify", "gourmet", or "healthy"

        Returns:
            Dict containing enhancement suggestions
        """
        enhancement_prompts = {
            "nutritional": "Analyze this recipe and provide nutritional information and suggestions to make it healthier.",
            "simplify": "Simplify this recipe to use fewer ingredients and reduce preparation time.",
            "gourmet": "Suggest ways to elevate this recipe with gourmet techniques and presentation tips.",
            "healthy": "Modify this recipe to reduce calories, sodium, and unhealthy fats while maintaining flavor.",
        }

        enhancement_instruction = enhancement_prompts.get(
            enhancement_type,
            enhancement_prompts["nutritional"],
        )

        prompt = f"""{enhancement_instruction}

Recipe:
{recipe}

Provide specific, actionable suggestions in a clear format."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert culinary consultant with deep knowledge of nutrition, cooking techniques, and food science.",
            },
            {"role": "user", "content": prompt},
        ]

        response_text = self._call_gpt(messages)

        return {
            "status": "success",
            "enhancement_type": enhancement_type,
            "original_recipe": recipe,
            "suggestions": response_text,
        }

    def get_pairing_suggestions(
        self, main_dish: str, meal_type: str = "dinner"
    ) -> Dict[str, Any]:
        """
        Get AI suggestions for food and wine pairings.

        Args:
            main_dish: The main dish to find pairings for
            meal_type: Type of meal ("breakfast", "lunch", "dinner")

        Returns:
            Dict containing pairing suggestions
        """
        prompt = f"""You are a professional sommelier and culinary expert. Based on the following main dish and meal type,
suggest appropriate side dishes, beverages, and wine pairings.

Main Dish: {main_dish}
Meal Type: {meal_type}

Provide:
1. 3 side dish recommendations with brief descriptions
2. 3 beverage recommendations (including wine options if appropriate)
3. Explanation of why these pairings work together
4. Serving temperature and plating suggestions

Format clearly with sections."""

        messages = [
            {
                "role": "system",
                "content": "You are an expert sommelier and food pairing specialist with years of experience in fine dining.",
            },
            {"role": "user", "content": prompt},
        ]

        response_text = self._call_gpt(messages)

        return {
            "status": "success",
            "main_dish": main_dish,
            "meal_type": meal_type,
            "pairings": response_text,
        }

    def analyze_dietary_impact(
        self, meal_description: str
    ) -> Dict[str, Any]:
        """
        Analyze the dietary and nutritional impact of a meal.

        Args:
            meal_description: Description of the meal to analyze

        Returns:
            Dict containing nutritional analysis and recommendations
        """
        prompt = f"""Analyze the following meal description and provide a comprehensive nutritional assessment.

Meal: {meal_description}

Provide:
1. Estimated macronutrient breakdown (proteins, carbs, fats)
2. Estimated calories
3. Key nutrients present
4. Potential deficiencies
5. Health recommendations
6. Impact on common dietary goals (weight loss, muscle gain, etc.)

Be specific and data-driven in your analysis."""

        messages = [
            {
                "role": "system",
                "content": "You are a certified nutritionist and dietitian with expertise in meal analysis and dietary guidance.",
            },
            {"role": "user", "content": prompt},
        ]

        response_text = self._call_gpt(messages)

        return {
            "status": "success",
            "meal_analyzed": meal_description,
            "analysis": response_text,
        }

    def get_shopping_list(
        self, meals: List[str], servings: int = 1
    ) -> Dict[str, Any]:
        """
        Generate a consolidated shopping list for multiple meals.

        Args:
            meals: List of meal names or recipes
            servings: Number of servings to prepare

        Returns:
            Dict containing organized shopping list
        """
        meals_text = "\n".join([f"- {meal}" for meal in meals])

        prompt = f"""Generate a consolidated and organized shopping list for the following meals.
Plan for {servings} serving(s).

Meals:
{meals_text}

Provide:
1. Organized list by category (produce, proteins, dairy, pantry, etc.)
2. Quantities needed
3. Estimated costs
4. Storage tips for ingredients
5. Suggested brands (optional, high-quality picks)
6. Notes on seasonal alternatives

Format as a practical shopping list."""

        messages = [
            {
                "role": "system",
                "content": "You are a professional chef and meal planner who creates efficient and cost-effective shopping lists.",
            },
            {"role": "user", "content": prompt},
        ]

        response_text = self._call_gpt(messages)

        return {
            "status": "success",
            "meals": meals,
            "servings": servings,
            "shopping_list": response_text,
        }


# Helper function for easy integration
def create_openai_integration(
    api_key: Optional[str] = None,
    model: str = "gpt-4",
    temperature: float = 0.7,
    max_tokens: int = 500,
) -> OpenAIIntegration:
    """
    Factory function to create an OpenAI integration instance.

    Args:
        api_key: OpenAI API key
        model: GPT model to use
        temperature: Response creativity level
        max_tokens: Maximum response length

    Returns:
        OpenAIIntegration instance
    """
    config = OpenAIConfig(
        api_key=api_key,
        model=model,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return OpenAIIntegration(config)
