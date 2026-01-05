"""
Core data models for the Food Agent App.

This module defines the database models for:
- Users
- Recipes
- Meal Plans
- Shopping Lists
- Daily Suggestions
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum


# ============================================================================
# Enums
# ============================================================================

class DietaryPreference(str, Enum):
    """Dietary preferences for users and recipes."""
    OMNIVORE = "omnivore"
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    KETO = "keto"
    PALEO = "paleo"
    PESCATARIAN = "pescatarian"


class MealType(str, Enum):
    """Types of meals."""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    DESSERT = "dessert"


class DifficultyLevel(str, Enum):
    """Recipe difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class ShoppingListStatus(str, Enum):
    """Shopping list status."""
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


# ============================================================================
# User Models
# ============================================================================

class User(BaseModel):
    """User model containing profile and preferences."""
    
    id: str = Field(..., description="Unique user identifier")
    email: str = Field(..., description="User email address")
    username: str = Field(..., description="User's display name")
    dietary_preferences: List[DietaryPreference] = Field(
        default_factory=list,
        description="List of dietary preferences"
    )
    allergies: List[str] = Field(
        default_factory=list,
        description="List of food allergies"
    )
    cuisine_preferences: List[str] = Field(
        default_factory=list,
        description="Preferred cuisines (e.g., Italian, Asian, Mexican)"
    )
    favorite_recipes: List[str] = Field(
        default_factory=list,
        description="List of favorite recipe IDs"
    )
    disliked_ingredients: List[str] = Field(
        default_factory=list,
        description="List of ingredients user dislikes"
    )
    weekly_meal_plan_preference: int = Field(
        default=7,
        description="Preferred number of days for meal planning"
    )
    budget_per_week: Optional[float] = Field(
        default=None,
        description="Weekly budget for groceries"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Account creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last profile update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "user_123",
                "email": "user@example.com",
                "username": "john_doe",
                "dietary_preferences": ["vegetarian"],
                "allergies": ["peanuts"],
                "cuisine_preferences": ["Italian", "Asian"],
                "favorite_recipes": ["recipe_1", "recipe_2"],
                "disliked_ingredients": ["mushrooms"],
                "weekly_meal_plan_preference": 7,
                "budget_per_week": 100.0
            }
        }


# ============================================================================
# Ingredient Models
# ============================================================================

class Ingredient(BaseModel):
    """Model for recipe ingredients."""
    
    name: str = Field(..., description="Ingredient name")
    quantity: float = Field(..., description="Amount needed")
    unit: str = Field(..., description="Unit of measurement (e.g., cups, grams, oz)")
    calories_per_unit: Optional[float] = Field(
        default=None,
        description="Calories per unit of ingredient"
    )
    cost_per_unit: Optional[float] = Field(
        default=None,
        description="Cost per unit of ingredient"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "name": "olive oil",
                "quantity": 2,
                "unit": "tablespoons",
                "calories_per_unit": 120,
                "cost_per_unit": 0.25
            }
        }


# ============================================================================
# Recipe Models
# ============================================================================

class Recipe(BaseModel):
    """Recipe model containing all recipe information."""
    
    id: str = Field(..., description="Unique recipe identifier")
    name: str = Field(..., description="Recipe name")
    description: str = Field(..., description="Recipe description")
    meal_type: MealType = Field(..., description="Type of meal")
    cuisine: str = Field(..., description="Cuisine type (e.g., Italian, Asian)")
    difficulty: DifficultyLevel = Field(..., description="Recipe difficulty")
    prep_time_minutes: int = Field(..., description="Preparation time in minutes")
    cook_time_minutes: int = Field(..., description="Cooking time in minutes")
    servings: int = Field(default=4, description="Number of servings")
    ingredients: List[Ingredient] = Field(..., description="List of ingredients")
    instructions: List[str] = Field(..., description="Step-by-step cooking instructions")
    dietary_tags: List[DietaryPreference] = Field(
        default_factory=list,
        description="Applicable dietary preferences"
    )
    estimated_cost: float = Field(..., description="Estimated total cost to prepare")
    estimated_calories: float = Field(..., description="Estimated calories per serving")
    rating: Optional[float] = Field(
        default=None,
        ge=0,
        le=5,
        description="Recipe rating out of 5"
    )
    number_of_ratings: int = Field(
        default=0,
        description="Number of ratings received"
    )
    images: List[str] = Field(
        default_factory=list,
        description="URLs to recipe images"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Recipe creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "recipe_123",
                "name": "Vegetarian Pasta Primavera",
                "description": "A light and colorful pasta dish with fresh vegetables",
                "meal_type": "dinner",
                "cuisine": "Italian",
                "difficulty": "easy",
                "prep_time_minutes": 10,
                "cook_time_minutes": 20,
                "servings": 4,
                "ingredients": [
                    {
                        "name": "pasta",
                        "quantity": 1,
                        "unit": "pound",
                        "calories_per_unit": 1700,
                        "cost_per_unit": 2.0
                    }
                ],
                "instructions": ["Boil water", "Cook pasta"],
                "dietary_tags": ["vegetarian"],
                "estimated_cost": 12.50,
                "estimated_calories": 350
            }
        }


# ============================================================================
# Meal Plan Models
# ============================================================================

class MealPlanDay(BaseModel):
    """Model for a single day in a meal plan."""
    
    day: int = Field(..., description="Day number (1-7)")
    date: datetime = Field(..., description="Calendar date")
    breakfast: Optional[str] = Field(
        default=None,
        description="Recipe ID for breakfast"
    )
    lunch: Optional[str] = Field(
        default=None,
        description="Recipe ID for lunch"
    )
    dinner: Optional[str] = Field(
        default=None,
        description="Recipe ID for dinner"
    )
    snacks: List[str] = Field(
        default_factory=list,
        description="Recipe IDs for snacks"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes for this day"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "day": 1,
                "date": "2026-01-06T00:00:00",
                "breakfast": "recipe_breakfast_1",
                "lunch": "recipe_lunch_1",
                "dinner": "recipe_dinner_1",
                "snacks": ["recipe_snack_1"],
                "notes": "Light dinner preferred"
            }
        }


class MealPlan(BaseModel):
    """Meal plan model for organizing meals over a period."""
    
    id: str = Field(..., description="Unique meal plan identifier")
    user_id: str = Field(..., description="User who owns this meal plan")
    name: str = Field(..., description="Name of the meal plan")
    description: Optional[str] = Field(
        default=None,
        description="Description of the meal plan"
    )
    start_date: datetime = Field(..., description="Meal plan start date")
    end_date: datetime = Field(..., description="Meal plan end date")
    days: List[MealPlanDay] = Field(..., description="List of planned days")
    total_estimated_cost: float = Field(
        default=0,
        description="Total estimated cost of the meal plan"
    )
    total_estimated_calories: float = Field(
        default=0,
        description="Total estimated calories for the meal plan"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Meal plan creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last meal plan update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "mealplan_123",
                "user_id": "user_123",
                "name": "Weekly Healthy Eating Plan",
                "description": "A nutritious meal plan for the week",
                "start_date": "2026-01-06T00:00:00",
                "end_date": "2026-01-12T00:00:00",
                "days": [],
                "total_estimated_cost": 87.50,
                "total_estimated_calories": 12250
            }
        }


# ============================================================================
# Shopping List Models
# ============================================================================

class ShoppingListItem(BaseModel):
    """Model for an item in a shopping list."""
    
    id: str = Field(..., description="Unique item identifier")
    name: str = Field(..., description="Item name")
    quantity: float = Field(..., description="Quantity needed")
    unit: str = Field(..., description="Unit of measurement")
    category: str = Field(
        default="other",
        description="Category (e.g., produce, dairy, meat)"
    )
    estimated_cost: Optional[float] = Field(
        default=None,
        description="Estimated cost of this item"
    )
    purchased: bool = Field(
        default=False,
        description="Whether item has been purchased"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Additional notes about this item"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "item_123",
                "name": "tomatoes",
                "quantity": 4,
                "unit": "medium",
                "category": "produce",
                "estimated_cost": 3.50,
                "purchased": False,
                "notes": "Fresh, preferably organic"
            }
        }


class ShoppingList(BaseModel):
    """Shopping list model for organizing groceries to purchase."""
    
    id: str = Field(..., description="Unique shopping list identifier")
    user_id: str = Field(..., description="User who owns this shopping list")
    meal_plan_id: Optional[str] = Field(
        default=None,
        description="Associated meal plan ID if auto-generated from meal plan"
    )
    name: str = Field(..., description="Name of the shopping list")
    items: List[ShoppingListItem] = Field(
        default_factory=list,
        description="List of shopping items"
    )
    status: ShoppingListStatus = Field(
        default=ShoppingListStatus.ACTIVE,
        description="Current status of the shopping list"
    )
    total_estimated_cost: float = Field(
        default=0,
        description="Total estimated cost of all items"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Shopping list creation timestamp"
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last shopping list update timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "shoplist_123",
                "user_id": "user_123",
                "meal_plan_id": "mealplan_123",
                "name": "Weekly Groceries",
                "items": [],
                "status": "active",
                "total_estimated_cost": 87.50,
                "created_at": "2026-01-05T14:16:21"
            }
        }


# ============================================================================
# Daily Suggestion Models
# ============================================================================

class DailySuggestion(BaseModel):
    """Daily meal suggestion based on user preferences."""
    
    id: str = Field(..., description="Unique suggestion identifier")
    user_id: str = Field(..., description="User who receives this suggestion")
    date: datetime = Field(..., description="Date of the suggestion")
    breakfast_recipe: Optional[Recipe] = Field(
        default=None,
        description="Suggested breakfast recipe"
    )
    breakfast_recipe_id: Optional[str] = Field(
        default=None,
        description="ID of suggested breakfast recipe"
    )
    lunch_recipe: Optional[Recipe] = Field(
        default=None,
        description="Suggested lunch recipe"
    )
    lunch_recipe_id: Optional[str] = Field(
        default=None,
        description="ID of suggested lunch recipe"
    )
    dinner_recipe: Optional[Recipe] = Field(
        default=None,
        description="Suggested dinner recipe"
    )
    dinner_recipe_id: Optional[str] = Field(
        default=None,
        description="ID of suggested dinner recipe"
    )
    snack_recipes: List[Recipe] = Field(
        default_factory=list,
        description="Suggested snack recipes"
    )
    snack_recipe_ids: List[str] = Field(
        default_factory=list,
        description="IDs of suggested snack recipes"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="AI reasoning for these suggestions"
    )
    total_calories: float = Field(
        default=0,
        description="Total estimated calories for the day"
    )
    estimated_cost: float = Field(
        default=0,
        description="Total estimated cost for the day"
    )
    accepted: bool = Field(
        default=False,
        description="Whether user accepted these suggestions"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Suggestion creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "suggestion_123",
                "user_id": "user_123",
                "date": "2026-01-06T00:00:00",
                "breakfast_recipe_id": "recipe_breakfast_1",
                "lunch_recipe_id": "recipe_lunch_1",
                "dinner_recipe_id": "recipe_dinner_1",
                "snack_recipe_ids": ["recipe_snack_1"],
                "reasoning": "Selected based on your vegetarian preference and Italian cuisine",
                "total_calories": 2100,
                "estimated_cost": 18.50,
                "accepted": False
            }
        }


# ============================================================================
# Batch Suggestion Models
# ============================================================================

class BatchDailySuggestions(BaseModel):
    """Batch of daily suggestions for multiple days."""
    
    id: str = Field(..., description="Unique batch identifier")
    user_id: str = Field(..., description="User who receives these suggestions")
    suggestions: List[DailySuggestion] = Field(
        ...,
        description="List of daily suggestions"
    )
    start_date: datetime = Field(..., description="Start date of suggestions")
    end_date: datetime = Field(..., description="End date of suggestions")
    total_cost: float = Field(
        default=0,
        description="Total estimated cost for all days"
    )
    average_daily_cost: float = Field(
        default=0,
        description="Average daily cost"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Batch creation timestamp"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": "batch_123",
                "user_id": "user_123",
                "suggestions": [],
                "start_date": "2026-01-06T00:00:00",
                "end_date": "2026-01-12T00:00:00",
                "total_cost": 130.00,
                "average_daily_cost": 18.57
            }
        }
