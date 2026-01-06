"""
Recipe Service Module

Provides comprehensive recipe management, search, filtering, and AI-powered enhancement capabilities
for the food-agent-app. This service handles all recipe-related operations including CRUD operations,
advanced search and filtering, and AI-powered recipe enhancements.
"""

import logging
from typing import List, Dict, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
from dataclasses import dataclass, asdict
import json
import re
from abc import ABC, abstractmethod

# Configure logging
logger = logging.getLogger(__name__)


class DietaryRestriction(str, Enum):
    """Enum for dietary restrictions."""
    VEGAN = "vegan"
    VEGETARIAN = "vegetarian"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    NUT_FREE = "nut_free"
    KETO = "keto"
    PALEO = "paleo"
    LOW_CARB = "low_carb"
    HALAL = "halal"
    KOSHER = "kosher"


class CuisineType(str, Enum):
    """Enum for cuisine types."""
    ITALIAN = "italian"
    ASIAN = "asian"
    MEXICAN = "mexican"
    INDIAN = "indian"
    MEDITERRANEAN = "mediterranean"
    AMERICAN = "american"
    FRENCH = "french"
    THAI = "thai"
    JAPANESE = "japanese"
    MIDDLE_EASTERN = "middle_eastern"
    FUSION = "fusion"


class DifficultyLevel(str, Enum):
    """Enum for recipe difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


@dataclass
class Ingredient:
    """Represents a recipe ingredient."""
    name: str
    amount: float
    unit: str
    optional: bool = False
    substitutes: List[str] = None

    def __post_init__(self):
        if self.substitutes is None:
            self.substitutes = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert ingredient to dictionary."""
        return asdict(self)


@dataclass
class NutritionInfo:
    """Represents nutritional information per serving."""
    calories: float
    protein_g: float
    carbs_g: float
    fat_g: float
    fiber_g: float
    sodium_mg: float

    def to_dict(self) -> Dict[str, float]:
        """Convert nutrition info to dictionary."""
        return asdict(self)


@dataclass
class Recipe:
    """Represents a recipe with all its attributes."""
    id: str
    name: str
    description: str
    ingredients: List[Ingredient]
    instructions: List[str]
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    cuisine_type: CuisineType
    difficulty_level: DifficultyLevel
    tags: List[str]
    dietary_restrictions: List[DietaryRestriction]
    nutrition_info: Optional[NutritionInfo] = None
    images: List[str] = None
    author: str = "Unknown"
    created_at: datetime = None
    updated_at: datetime = None
    rating: float = 0.0
    review_count: int = 0
    source_url: Optional[str] = None
    yield_text: str = "servings"

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()

    @property
    def total_time_minutes(self) -> int:
        """Calculate total cooking time."""
        return self.prep_time_minutes + self.cook_time_minutes

    def to_dict(self) -> Dict[str, Any]:
        """Convert recipe to dictionary."""
        recipe_dict = asdict(self)
        recipe_dict['ingredients'] = [ing.to_dict() for ing in self.ingredients]
        if self.nutrition_info:
            recipe_dict['nutrition_info'] = self.nutrition_info.to_dict()
        recipe_dict['created_at'] = self.created_at.isoformat()
        recipe_dict['updated_at'] = self.updated_at.isoformat()
        recipe_dict['cuisine_type'] = self.cuisine_type.value
        recipe_dict['difficulty_level'] = self.difficulty_level.value
        recipe_dict['dietary_restrictions'] = [dr.value for dr in self.dietary_restrictions]
        return recipe_dict


class RecipeEnhancer(ABC):
    """Abstract base class for recipe enhancement strategies."""

    @abstractmethod
    def enhance(self, recipe: Recipe) -> Recipe:
        """Enhance recipe with AI-powered improvements."""
        pass


class AIRecipeEnhancer(RecipeEnhancer):
    """AI-powered recipe enhancement implementation."""

    def __init__(self, ai_model=None):
        """Initialize AI recipe enhancer."""
        self.ai_model = ai_model
        self.enhancements_applied = []

    def enhance(self, recipe: Recipe) -> Recipe:
        """
        Enhance recipe with AI-powered improvements.
        Implements intelligent recipe optimization.
        """
        logger.info(f"Enhancing recipe: {recipe.name}")
        
        # Enhance instructions clarity
        recipe.instructions = self._improve_instructions(recipe.instructions)
        
        # Suggest ingredient substitutes
        recipe = self._add_ingredient_substitutes(recipe)
        
        # Estimate and optimize nutrition info
        if not recipe.nutrition_info:
            recipe.nutrition_info = self._estimate_nutrition(recipe)
        
        # Generate SEO-friendly tags
        recipe.tags = self._generate_enhanced_tags(recipe)
        
        recipe.updated_at = datetime.utcnow()
        self.enhancements_applied.append({
            'recipe_id': recipe.id,
            'timestamp': datetime.utcnow().isoformat(),
            'enhancements': ['instructions', 'substitutes', 'nutrition', 'tags']
        })
        
        return recipe

    def _improve_instructions(self, instructions: List[str]) -> List[str]:
        """Improve clarity and completeness of cooking instructions."""
        improved = []
        for i, instruction in enumerate(instructions, 1):
            # Add step numbering if not present
            if not instruction.startswith(f"{i}.") and not instruction.startswith(f"Step {i}"):
                instruction = f"Step {i}: {instruction}"
            
            # Capitalize first letter after step number
            if ":" in instruction:
                parts = instruction.split(":", 1)
                parts[1] = parts[1].strip().capitalize()
                instruction = ":".join(parts)
            
            improved.append(instruction)
        
        return improved

    def _add_ingredient_substitutes(self, recipe: Recipe) -> Recipe:
        """Add intelligent ingredient substitutes based on common allergies."""
        substitute_map = {
            "milk": ["almond milk", "oat milk", "soy milk", "coconut milk"],
            "butter": ["coconut oil", "olive oil", "vegan butter"],
            "egg": ["flax egg", "chia egg", "applesauce", "banana"],
            "wheat flour": ["gluten-free flour", "almond flour", "coconut flour"],
            "sugar": ["honey", "maple syrup", "agave nectar"],
            "salt": ["sea salt", "himalayan salt"],
        }
        
        for ingredient in recipe.ingredients:
            ingredient_lower = ingredient.name.lower()
            for original, substitutes in substitute_map.items():
                if original in ingredient_lower:
                    ingredient.substitutes = substitutes
                    break
        
        return recipe

    def _estimate_nutrition(self, recipe: Recipe) -> NutritionInfo:
        """Estimate nutrition information based on ingredients."""
        # Simplified estimation logic - in production, use a nutrition database
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        total_sodium = 0
        
        # Mock nutrition database (in production, use USDA FoodData Central or similar)
        nutrition_db = {
            "oil": {"calories": 120, "protein": 0, "carbs": 0, "fat": 14, "fiber": 0, "sodium": 0},
            "salt": {"calories": 0, "protein": 0, "carbs": 0, "fat": 0, "fiber": 0, "sodium": 2300},
            "flour": {"calories": 455, "protein": 12.3, "carbs": 95.4, "fat": 1.3, "fiber": 3.7, "sodium": 2},
            "sugar": {"calories": 387, "protein": 0, "carbs": 100, "fat": 0, "fiber": 0, "sodium": 2},
        }
        
        for ingredient in recipe.ingredients:
            ing_lower = ingredient.name.lower()
            for key, nutrition in nutrition_db.items():
                if key in ing_lower:
                    multiplier = ingredient.amount / recipe.servings
                    total_calories += nutrition["calories"] * multiplier
                    total_protein += nutrition["protein"] * multiplier
                    total_carbs += nutrition["carbs"] * multiplier
                    total_fat += nutrition["fat"] * multiplier
                    total_fiber += nutrition["fiber"] * multiplier
                    total_sodium += nutrition["sodium"] * multiplier
                    break
        
        return NutritionInfo(
            calories=round(total_calories, 1),
            protein_g=round(total_protein, 1),
            carbs_g=round(total_carbs, 1),
            fat_g=round(total_fat, 1),
            fiber_g=round(total_fiber, 1),
            sodium_mg=round(total_sodium, 1)
        )

    def _generate_enhanced_tags(self, recipe: Recipe) -> List[str]:
        """Generate SEO-friendly and descriptive tags."""
        tags = set(recipe.tags)
        
        # Add time-based tags
        if recipe.total_time_minutes <= 30:
            tags.add("quick")
        if recipe.total_time_minutes <= 15:
            tags.add("15-minute-meal")
        if recipe.prep_time_minutes == 0:
            tags.add("no-prep")
        
        # Add difficulty tags
        tags.add(recipe.difficulty_level.value)
        
        # Add dietary tags
        for restriction in recipe.dietary_restrictions:
            tags.add(restriction.value)
        
        # Add cuisine tags
        tags.add(f"{recipe.cuisine_type.value}-cuisine")
        
        # Add meal type tags
        tags.add("homemade")
        if recipe.total_time_minutes <= 60:
            tags.add("weeknight-dinner")
        
        return list(tags)


class RecipeFilter:
    """Advanced recipe filtering engine."""

    def __init__(self):
        """Initialize recipe filter."""
        self.filters = {}

    def by_cuisine(self, cuisine: CuisineType) -> 'RecipeFilter':
        """Filter by cuisine type."""
        self.filters['cuisine'] = cuisine
        return self

    def by_difficulty(self, difficulty: DifficultyLevel) -> 'RecipeFilter':
        """Filter by difficulty level."""
        self.filters['difficulty'] = difficulty
        return self

    def by_prep_time(self, max_minutes: int) -> 'RecipeFilter':
        """Filter by maximum preparation time."""
        self.filters['prep_time'] = max_minutes
        return self

    def by_cook_time(self, max_minutes: int) -> 'RecipeFilter':
        """Filter by maximum cooking time."""
        self.filters['cook_time'] = max_minutes
        return self

    def by_total_time(self, max_minutes: int) -> 'RecipeFilter':
        """Filter by maximum total time."""
        self.filters['total_time'] = max_minutes
        return self

    def by_dietary_restrictions(self, restrictions: List[DietaryRestriction]) -> 'RecipeFilter':
        """Filter by dietary restrictions."""
        self.filters['dietary_restrictions'] = restrictions
        return self

    def by_servings(self, servings: int) -> 'RecipeFilter':
        """Filter by number of servings."""
        self.filters['servings'] = servings
        return self

    def by_ingredients(self, ingredients: List[str]) -> 'RecipeFilter':
        """Filter by required ingredients."""
        self.filters['ingredients'] = [ing.lower() for ing in ingredients]
        return self

    def exclude_ingredients(self, ingredients: List[str]) -> 'RecipeFilter':
        """Filter out recipes with specific ingredients."""
        self.filters['exclude_ingredients'] = [ing.lower() for ing in ingredients]
        return self

    def by_rating(self, min_rating: float) -> 'RecipeFilter':
        """Filter by minimum rating."""
        self.filters['rating'] = min_rating
        return self

    def by_tags(self, tags: List[str]) -> 'RecipeFilter':
        """Filter by tags."""
        self.filters['tags'] = [tag.lower() for tag in tags]
        return self

    def apply(self, recipes: List[Recipe]) -> List[Recipe]:
        """Apply all filters to a list of recipes."""
        filtered = recipes
        
        if 'cuisine' in self.filters:
            filtered = [r for r in filtered if r.cuisine_type == self.filters['cuisine']]
        
        if 'difficulty' in self.filters:
            filtered = [r for r in filtered if r.difficulty_level == self.filters['difficulty']]
        
        if 'prep_time' in self.filters:
            filtered = [r for r in filtered if r.prep_time_minutes <= self.filters['prep_time']]
        
        if 'cook_time' in self.filters:
            filtered = [r for r in filtered if r.cook_time_minutes <= self.filters['cook_time']]
        
        if 'total_time' in self.filters:
            filtered = [r for r in filtered if r.total_time_minutes <= self.filters['total_time']]
        
        if 'dietary_restrictions' in self.filters:
            filtered = [r for r in filtered 
                       if all(dr in r.dietary_restrictions for dr in self.filters['dietary_restrictions'])]
        
        if 'servings' in self.filters:
            filtered = [r for r in filtered if r.servings >= self.filters['servings']]
        
        if 'ingredients' in self.filters:
            filtered = [r for r in filtered 
                       if self._has_ingredients(r, self.filters['ingredients'])]
        
        if 'exclude_ingredients' in self.filters:
            filtered = [r for r in filtered 
                       if not self._has_ingredients(r, self.filters['exclude_ingredients'])]
        
        if 'rating' in self.filters:
            filtered = [r for r in filtered if r.rating >= self.filters['rating']]
        
        if 'tags' in self.filters:
            filtered = [r for r in filtered 
                       if self._has_tags(r, self.filters['tags'])]
        
        return filtered

    def _has_ingredients(self, recipe: Recipe, ingredients: List[str]) -> bool:
        """Check if recipe contains all required ingredients."""
        recipe_ingredients = [ing.name.lower() for ing in recipe.ingredients]
        return all(any(req_ing in rec_ing for rec_ing in recipe_ingredients) for req_ing in ingredients)

    def _has_tags(self, recipe: Recipe, tags: List[str]) -> bool:
        """Check if recipe contains any of the required tags."""
        recipe_tags = [tag.lower() for tag in recipe.tags]
        return any(tag in recipe_tags for tag in tags)

    def reset(self) -> 'RecipeFilter':
        """Reset all filters."""
        self.filters = {}
        return self


class RecipeSearchEngine:
    """Advanced recipe search engine with ranking."""

    def __init__(self):
        """Initialize search engine."""
        self.recipes: Dict[str, Recipe] = {}

    def index_recipe(self, recipe: Recipe) -> None:
        """Index a recipe for searching."""
        self.recipes[recipe.id] = recipe
        logger.info(f"Indexed recipe: {recipe.name}")

    def search(self, query: str, limit: int = 10) -> List[Tuple[Recipe, float]]:
        """
        Search recipes using full-text search with ranking.
        
        Returns list of (recipe, relevance_score) tuples.
        """
        if not query.strip():
            return []
        
        query_lower = query.lower()
        results = []
        
        for recipe in self.recipes.values():
            score = self._calculate_relevance_score(recipe, query_lower)
            if score > 0:
                results.append((recipe, score))
        
        # Sort by relevance score
        results.sort(key=lambda x: x[1], reverse=True)
        
        return results[:limit]

    def _calculate_relevance_score(self, recipe: Recipe, query: str) -> float:
        """Calculate relevance score for a recipe."""
        score = 0.0
        
        # Check recipe name (highest weight)
        if query in recipe.name.lower():
            score += 50
        
        # Check description
        if query in recipe.description.lower():
            score += 30
        
        # Check tags
        for tag in recipe.tags:
            if query in tag.lower():
                score += 20
        
        # Check ingredients
        for ingredient in recipe.ingredients:
            if query in ingredient.name.lower():
                score += 15
        
        # Check cuisine type
        if query in recipe.cuisine_type.value:
            score += 10
        
        # Boost highly-rated recipes
        if recipe.rating > 4.5:
            score *= 1.2
        
        return score


class RecipeService:
    """Main recipe service with complete recipe management capabilities."""

    def __init__(self, ai_enhancer: Optional[RecipeEnhancer] = None):
        """
        Initialize recipe service.
        
        Args:
            ai_enhancer: Optional AI recipe enhancer instance
        """
        self.recipes: Dict[str, Recipe] = {}
        self.search_engine = RecipeSearchEngine()
        self.ai_enhancer = ai_enhancer or AIRecipeEnhancer()
        self.filter = RecipeFilter()
        logger.info("RecipeService initialized")

    def create_recipe(self, recipe: Recipe, enhance: bool = False) -> Recipe:
        """
        Create a new recipe.
        
        Args:
            recipe: Recipe instance to create
            enhance: Whether to apply AI enhancement
            
        Returns:
            Created recipe
        """
        if recipe.id in self.recipes:
            raise ValueError(f"Recipe with ID {recipe.id} already exists")
        
        if enhance:
            recipe = self.ai_enhancer.enhance(recipe)
        
        self.recipes[recipe.id] = recipe
        self.search_engine.index_recipe(recipe)
        logger.info(f"Created recipe: {recipe.name}")
        
        return recipe

    def get_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """Get a recipe by ID."""
        return self.recipes.get(recipe_id)

    def update_recipe(self, recipe_id: str, updates: Dict[str, Any]) -> Optional[Recipe]:
        """
        Update a recipe with provided updates.
        
        Args:
            recipe_id: ID of recipe to update
            updates: Dictionary of updates
            
        Returns:
            Updated recipe or None if not found
        """
        if recipe_id not in self.recipes:
            return None
        
        recipe = self.recipes[recipe_id]
        
        # Update allowed fields
        allowed_fields = {
            'name', 'description', 'ingredients', 'instructions',
            'prep_time_minutes', 'cook_time_minutes', 'servings',
            'tags', 'dietary_restrictions', 'nutrition_info'
        }
        
        for field, value in updates.items():
            if field in allowed_fields:
                setattr(recipe, field, value)
        
        recipe.updated_at = datetime.utcnow()
        logger.info(f"Updated recipe: {recipe.name}")
        
        return recipe

    def delete_recipe(self, recipe_id: str) -> bool:
        """Delete a recipe."""
        if recipe_id in self.recipes:
            del self.recipes[recipe_id]
            logger.info(f"Deleted recipe with ID: {recipe_id}")
            return True
        return False

    def list_recipes(self, limit: int = 100, offset: int = 0) -> List[Recipe]:
        """List all recipes with pagination."""
        recipes_list = list(self.recipes.values())
        recipes_list.sort(key=lambda r: r.created_at, reverse=True)
        return recipes_list[offset:offset + limit]

    def search_recipes(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search recipes by query string.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of recipes with relevance scores
        """
        results = self.search_engine.search(query, limit)
        return [
            {
                'recipe': result[0].to_dict(),
                'relevance_score': result[1]
            }
            for result in results
        ]

    def filter_recipes(self, **filter_criteria) -> List[Recipe]:
        """
        Filter recipes using advanced filter criteria.
        
        Supported criteria:
            - cuisine: CuisineType
            - difficulty: DifficultyLevel
            - prep_time: int (max minutes)
            - cook_time: int (max minutes)
            - total_time: int (max minutes)
            - dietary_restrictions: List[DietaryRestriction]
            - servings: int (minimum)
            - ingredients: List[str]
            - exclude_ingredients: List[str]
            - rating: float (minimum)
            - tags: List[str]
        """
        filter_obj = RecipeFilter()
        
        if 'cuisine' in filter_criteria:
            filter_obj.by_cuisine(filter_criteria['cuisine'])
        if 'difficulty' in filter_criteria:
            filter_obj.by_difficulty(filter_criteria['difficulty'])
        if 'prep_time' in filter_criteria:
            filter_obj.by_prep_time(filter_criteria['prep_time'])
        if 'cook_time' in filter_criteria:
            filter_obj.by_cook_time(filter_criteria['cook_time'])
        if 'total_time' in filter_criteria:
            filter_obj.by_total_time(filter_criteria['total_time'])
        if 'dietary_restrictions' in filter_criteria:
            filter_obj.by_dietary_restrictions(filter_criteria['dietary_restrictions'])
        if 'servings' in filter_criteria:
            filter_obj.by_servings(filter_criteria['servings'])
        if 'ingredients' in filter_criteria:
            filter_obj.by_ingredients(filter_criteria['ingredients'])
        if 'exclude_ingredients' in filter_criteria:
            filter_obj.exclude_ingredients(filter_criteria['exclude_ingredients'])
        if 'rating' in filter_criteria:
            filter_obj.by_rating(filter_criteria['rating'])
        if 'tags' in filter_criteria:
            filter_obj.by_tags(filter_criteria['tags'])
        
        return filter_obj.apply(list(self.recipes.values()))

    def enhance_recipe(self, recipe_id: str) -> Optional[Recipe]:
        """
        Apply AI-powered enhancements to a recipe.
        
        Args:
            recipe_id: ID of recipe to enhance
            
        Returns:
            Enhanced recipe or None if not found
        """
        if recipe_id not in self.recipes:
            return None
        
        recipe = self.recipes[recipe_id]
        enhanced = self.ai_enhancer.enhance(recipe)
        self.recipes[recipe_id] = enhanced
        
        return enhanced

    def get_recipe_recommendations(self, recipe_id: str, limit: int = 5) -> List[Recipe]:
        """
        Get recipe recommendations based on a similar recipe.
        
        Args:
            recipe_id: ID of reference recipe
            limit: Maximum number of recommendations
            
        Returns:
            List of similar recipes
        """
        if recipe_id not in self.recipes:
            return []
        
        reference = self.recipes[recipe_id]
        
        # Find similar recipes
        similar = []
        for recipe in self.recipes.values():
            if recipe.id == recipe_id:
                continue
            
            similarity_score = 0
            
            # Same cuisine type (highest weight)
            if recipe.cuisine_type == reference.cuisine_type:
                similarity_score += 30
            
            # Similar difficulty
            if recipe.difficulty_level == reference.difficulty_level:
                similarity_score += 20
            
            # Shared dietary restrictions
            shared_restrictions = len(set(recipe.dietary_restrictions) & 
                                      set(reference.dietary_restrictions))
            similarity_score += shared_restrictions * 10
            
            # Shared tags
            shared_tags = len(set(recipe.tags) & set(reference.tags))
            similarity_score += shared_tags * 5
            
            # Similar total time
            time_diff = abs(recipe.total_time_minutes - reference.total_time_minutes)
            if time_diff <= 15:
                similarity_score += 15
            elif time_diff <= 30:
                similarity_score += 10
            
            # Higher ratings
            if recipe.rating > 4.0:
                similarity_score *= 1.1
            
            similar.append((recipe, similarity_score))
        
        similar.sort(key=lambda x: x[1], reverse=True)
        return [recipe for recipe, _ in similar[:limit]]

    def get_statistics(self) -> Dict[str, Any]:
        """Get recipe collection statistics."""
        recipes_list = list(self.recipes.values())
        
        if not recipes_list:
            return {
                'total_recipes': 0,
                'average_rating': 0,
                'average_prep_time': 0,
                'average_cook_time': 0,
                'total_recipes': 0
            }
        
        avg_rating = sum(r.rating for r in recipes_list) / len(recipes_list)
        avg_prep = sum(r.prep_time_minutes for r in recipes_list) / len(recipes_list)
        avg_cook = sum(r.cook_time_minutes for r in recipes_list) / len(recipes_list)
        
        # Count cuisines
        cuisine_counts = {}
        for recipe in recipes_list:
            cuisine_counts[recipe.cuisine_type.value] = cuisine_counts.get(recipe.cuisine_type.value, 0) + 1
        
        # Count difficulty levels
        difficulty_counts = {}
        for recipe in recipes_list:
            difficulty_counts[recipe.difficulty_level.value] = difficulty_counts.get(recipe.difficulty_level.value, 0) + 1
        
        return {
            'total_recipes': len(recipes_list),
            'average_rating': round(avg_rating, 2),
            'average_prep_time_minutes': round(avg_prep, 1),
            'average_cook_time_minutes': round(avg_cook, 1),
            'cuisine_distribution': cuisine_counts,
            'difficulty_distribution': difficulty_counts,
            'total_reviews': sum(r.review_count for r in recipes_list)
        }

    def export_recipes(self, recipe_ids: Optional[List[str]] = None) -> str:
        """
        Export recipes as JSON.
        
        Args:
            recipe_ids: Specific recipe IDs to export (None for all)
            
        Returns:
            JSON string of recipes
        """
        if recipe_ids:
            recipes_to_export = [self.recipes[rid] for rid in recipe_ids if rid in self.recipes]
        else:
            recipes_to_export = list(self.recipes.values())
        
        recipes_dicts = [r.to_dict() for r in recipes_to_export]
        return json.dumps(recipes_dicts, indent=2)

    def import_recipes(self, json_data: str, enhance: bool = False) -> List[Recipe]:
        """
        Import recipes from JSON.
        
        Args:
            json_data: JSON string of recipes
            enhance: Whether to apply AI enhancement
            
        Returns:
            List of imported recipes
        """
        recipes_data = json.loads(json_data)
        imported_recipes = []
        
        for recipe_data in recipes_data:
            # Parse ingredients
            ingredients = [
                Ingredient(
                    name=ing['name'],
                    amount=ing['amount'],
                    unit=ing['unit'],
                    optional=ing.get('optional', False),
                    substitutes=ing.get('substitutes', [])
                )
                for ing in recipe_data.get('ingredients', [])
            ]
            
            # Parse nutrition info
            nutrition_data = recipe_data.get('nutrition_info')
            nutrition_info = None
            if nutrition_data:
                nutrition_info = NutritionInfo(**nutrition_data)
            
            # Create recipe
            recipe = Recipe(
                id=recipe_data['id'],
                name=recipe_data['name'],
                description=recipe_data['description'],
                ingredients=ingredients,
                instructions=recipe_data['instructions'],
                prep_time_minutes=recipe_data['prep_time_minutes'],
                cook_time_minutes=recipe_data['cook_time_minutes'],
                servings=recipe_data['servings'],
                cuisine_type=CuisineType(recipe_data['cuisine_type']),
                difficulty_level=DifficultyLevel(recipe_data['difficulty_level']),
                tags=recipe_data['tags'],
                dietary_restrictions=[DietaryRestriction(dr) for dr in recipe_data['dietary_restrictions']],
                nutrition_info=nutrition_info,
                images=recipe_data.get('images', []),
                author=recipe_data.get('author', 'Unknown'),
                rating=recipe_data.get('rating', 0.0),
                review_count=recipe_data.get('review_count', 0),
                source_url=recipe_data.get('source_url')
            )
            
            imported_recipes.append(self.create_recipe(recipe, enhance=enhance))
        
        logger.info(f"Imported {len(imported_recipes)} recipes")
        return imported_recipes
