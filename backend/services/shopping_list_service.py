"""
Shopping List Management Service

This module provides functionality for managing shopping lists in the food-agent-app.
It handles CRUD operations for shopping lists and items, including adding, removing,
updating, and organizing shopping list items.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum


class ItemCategory(Enum):
    """Categories for shopping list items."""
    PRODUCE = "produce"
    DAIRY = "dairy"
    MEAT = "meat"
    GRAINS = "grains"
    PANTRY = "pantry"
    FROZEN = "frozen"
    BEVERAGES = "beverages"
    OTHER = "other"


class ShoppingListItem:
    """Represents a single item in a shopping list."""
    
    def __init__(
        self,
        item_id: str,
        name: str,
        quantity: float,
        unit: str,
        category: ItemCategory = ItemCategory.OTHER,
        checked: bool = False,
        notes: Optional[str] = None
    ):
        """
        Initialize a shopping list item.
        
        Args:
            item_id: Unique identifier for the item
            name: Name of the item
            quantity: Quantity needed
            unit: Unit of measurement (e.g., 'kg', 'lbs', 'pieces')
            category: Category of the item
            checked: Whether the item has been purchased
            notes: Optional notes about the item
        """
        self.item_id = item_id
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.category = category
        self.checked = checked
        self.notes = notes
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary representation."""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "category": self.category.value,
            "checked": self.checked,
            "notes": self.notes,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
    
    def toggle_checked(self) -> None:
        """Toggle the checked status of the item."""
        self.checked = not self.checked
        self.updated_at = datetime.utcnow()


class ShoppingList:
    """Represents a shopping list with multiple items."""
    
    def __init__(
        self,
        list_id: str,
        name: str,
        user_id: str,
        description: Optional[str] = None
    ):
        """
        Initialize a shopping list.
        
        Args:
            list_id: Unique identifier for the list
            name: Name of the shopping list
            user_id: User who owns the list
            description: Optional description of the list
        """
        self.list_id = list_id
        self.name = name
        self.user_id = user_id
        self.description = description
        self.items: List[ShoppingListItem] = []
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert shopping list to dictionary representation."""
        return {
            "list_id": self.list_id,
            "name": self.name,
            "user_id": self.user_id,
            "description": self.description,
            "items": [item.to_dict() for item in self.items],
            "item_count": len(self.items),
            "checked_count": sum(1 for item in self.items if item.checked),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class ShoppingListService:
    """Service for managing shopping lists and their items."""
    
    def __init__(self):
        """Initialize the shopping list service."""
        # In-memory storage (would be replaced with database in production)
        self.shopping_lists: Dict[str, ShoppingList] = {}
        self.items_by_id: Dict[str, ShoppingListItem] = {}
    
    def create_shopping_list(
        self,
        list_id: str,
        name: str,
        user_id: str,
        description: Optional[str] = None
    ) -> ShoppingList:
        """
        Create a new shopping list.
        
        Args:
            list_id: Unique identifier for the list
            name: Name of the shopping list
            user_id: User who owns the list
            description: Optional description of the list
            
        Returns:
            The created ShoppingList object
            
        Raises:
            ValueError: If list_id already exists
        """
        if list_id in self.shopping_lists:
            raise ValueError(f"Shopping list with id '{list_id}' already exists")
        
        shopping_list = ShoppingList(list_id, name, user_id, description)
        self.shopping_lists[list_id] = shopping_list
        return shopping_list
    
    def get_shopping_list(self, list_id: str) -> Optional[ShoppingList]:
        """
        Retrieve a shopping list by ID.
        
        Args:
            list_id: The ID of the shopping list
            
        Returns:
            The ShoppingList object or None if not found
        """
        return self.shopping_lists.get(list_id)
    
    def get_user_shopping_lists(self, user_id: str) -> List[ShoppingList]:
        """
        Retrieve all shopping lists for a user.
        
        Args:
            user_id: The user ID
            
        Returns:
            List of ShoppingList objects belonging to the user
        """
        return [
            lst for lst in self.shopping_lists.values()
            if lst.user_id == user_id
        ]
    
    def update_shopping_list(
        self,
        list_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Optional[ShoppingList]:
        """
        Update a shopping list's metadata.
        
        Args:
            list_id: The ID of the shopping list
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            The updated ShoppingList object or None if not found
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return None
        
        if name:
            shopping_list.name = name
        if description is not None:
            shopping_list.description = description
        
        shopping_list.updated_at = datetime.utcnow()
        return shopping_list
    
    def delete_shopping_list(self, list_id: str) -> bool:
        """
        Delete a shopping list.
        
        Args:
            list_id: The ID of the shopping list
            
        Returns:
            True if deleted, False if not found
        """
        shopping_list = self.shopping_lists.pop(list_id, None)
        if shopping_list:
            # Clean up items associated with this list
            for item in shopping_list.items:
                self.items_by_id.pop(item.item_id, None)
            return True
        return False
    
    def add_item(
        self,
        list_id: str,
        item_id: str,
        name: str,
        quantity: float,
        unit: str,
        category: ItemCategory = ItemCategory.OTHER,
        notes: Optional[str] = None
    ) -> Optional[ShoppingListItem]:
        """
        Add an item to a shopping list.
        
        Args:
            list_id: The ID of the shopping list
            item_id: Unique identifier for the item
            name: Name of the item
            quantity: Quantity needed
            unit: Unit of measurement
            category: Category of the item
            notes: Optional notes about the item
            
        Returns:
            The created ShoppingListItem or None if list not found
            
        Raises:
            ValueError: If item_id already exists in the list
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return None
        
        if item_id in self.items_by_id:
            raise ValueError(f"Item with id '{item_id}' already exists")
        
        item = ShoppingListItem(
            item_id=item_id,
            name=name,
            quantity=quantity,
            unit=unit,
            category=category,
            notes=notes
        )
        
        shopping_list.items.append(item)
        self.items_by_id[item_id] = item
        shopping_list.updated_at = datetime.utcnow()
        
        return item
    
    def get_item(self, item_id: str) -> Optional[ShoppingListItem]:
        """
        Retrieve an item by ID.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            The ShoppingListItem or None if not found
        """
        return self.items_by_id.get(item_id)
    
    def update_item(
        self,
        item_id: str,
        name: Optional[str] = None,
        quantity: Optional[float] = None,
        unit: Optional[str] = None,
        category: Optional[ItemCategory] = None,
        notes: Optional[str] = None
    ) -> Optional[ShoppingListItem]:
        """
        Update a shopping list item.
        
        Args:
            item_id: The ID of the item
            name: New name (optional)
            quantity: New quantity (optional)
            unit: New unit (optional)
            category: New category (optional)
            notes: New notes (optional)
            
        Returns:
            The updated ShoppingListItem or None if not found
        """
        item = self.items_by_id.get(item_id)
        if not item:
            return None
        
        if name:
            item.name = name
        if quantity is not None:
            item.quantity = quantity
        if unit:
            item.unit = unit
        if category:
            item.category = category
        if notes is not None:
            item.notes = notes
        
        item.updated_at = datetime.utcnow()
        return item
    
    def remove_item(self, list_id: str, item_id: str) -> bool:
        """
        Remove an item from a shopping list.
        
        Args:
            list_id: The ID of the shopping list
            item_id: The ID of the item to remove
            
        Returns:
            True if removed, False if not found
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return False
        
        item = next((i for i in shopping_list.items if i.item_id == item_id), None)
        if item:
            shopping_list.items.remove(item)
            self.items_by_id.pop(item_id, None)
            shopping_list.updated_at = datetime.utcnow()
            return True
        
        return False
    
    def toggle_item_checked(self, item_id: str) -> Optional[ShoppingListItem]:
        """
        Toggle the checked status of an item.
        
        Args:
            item_id: The ID of the item
            
        Returns:
            The updated ShoppingListItem or None if not found
        """
        item = self.items_by_id.get(item_id)
        if item:
            item.toggle_checked()
            return item
        return None
    
    def get_items_by_category(
        self,
        list_id: str,
        category: ItemCategory
    ) -> List[ShoppingListItem]:
        """
        Get all items in a shopping list filtered by category.
        
        Args:
            list_id: The ID of the shopping list
            category: The category to filter by
            
        Returns:
            List of items in the specified category
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return []
        
        return [
            item for item in shopping_list.items
            if item.category == category
        ]
    
    def get_unchecked_items(self, list_id: str) -> List[ShoppingListItem]:
        """
        Get all unchecked items in a shopping list.
        
        Args:
            list_id: The ID of the shopping list
            
        Returns:
            List of unchecked items
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return []
        
        return [item for item in shopping_list.items if not item.checked]
    
    def get_checked_items(self, list_id: str) -> List[ShoppingListItem]:
        """
        Get all checked items in a shopping list.
        
        Args:
            list_id: The ID of the shopping list
            
        Returns:
            List of checked items
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return []
        
        return [item for item in shopping_list.items if item.checked]
    
    def clear_checked_items(self, list_id: str) -> int:
        """
        Remove all checked items from a shopping list.
        
        Args:
            list_id: The ID of the shopping list
            
        Returns:
            Number of items removed
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return 0
        
        checked_items = self.get_checked_items(list_id)
        removed_count = 0
        
        for item in checked_items:
            if self.remove_item(list_id, item.item_id):
                removed_count += 1
        
        return removed_count
    
    def duplicate_shopping_list(
        self,
        source_list_id: str,
        new_list_id: str,
        new_name: Optional[str] = None
    ) -> Optional[ShoppingList]:
        """
        Create a duplicate of an existing shopping list.
        
        Args:
            source_list_id: The ID of the list to duplicate
            new_list_id: The ID for the new list
            new_name: Optional new name for the duplicated list
            
        Returns:
            The new ShoppingList or None if source not found
        """
        source_list = self.shopping_lists.get(source_list_id)
        if not source_list:
            return None
        
        list_name = new_name or f"{source_list.name} (Copy)"
        new_list = self.create_shopping_list(
            new_list_id,
            list_name,
            source_list.user_id,
            source_list.description
        )
        
        # Copy all items to the new list
        for item in source_list.items:
            self.add_item(
                new_list_id,
                f"{new_list_id}_item_{len(new_list.items)}",
                item.name,
                item.quantity,
                item.unit,
                item.category,
                item.notes
            )
        
        return new_list
    
    def merge_shopping_lists(
        self,
        list_id_1: str,
        list_id_2: str,
        merged_list_id: str,
        merged_name: str
    ) -> Optional[ShoppingList]:
        """
        Merge two shopping lists into a new one.
        
        Args:
            list_id_1: ID of first list
            list_id_2: ID of second list
            merged_list_id: ID for the merged list
            merged_name: Name for the merged list
            
        Returns:
            The new merged ShoppingList or None if source lists not found
        """
        list_1 = self.shopping_lists.get(list_id_1)
        list_2 = self.shopping_lists.get(list_id_2)
        
        if not list_1 or not list_2:
            return None
        
        merged_list = self.create_shopping_list(
            merged_list_id,
            merged_name,
            list_1.user_id
        )
        
        # Add items from both lists
        item_count = 0
        for item in list_1.items + list_2.items:
            self.add_item(
                merged_list_id,
                f"{merged_list_id}_item_{item_count}",
                item.name,
                item.quantity,
                item.unit,
                item.category,
                item.notes
            )
            item_count += 1
        
        return merged_list
    
    def get_shopping_list_summary(self, list_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a shopping list with statistics.
        
        Args:
            list_id: The ID of the shopping list
            
        Returns:
            Dictionary with list summary or None if not found
        """
        shopping_list = self.shopping_lists.get(list_id)
        if not shopping_list:
            return None
        
        items_by_category = {}
        for category in ItemCategory:
            items = self.get_items_by_category(list_id, category)
            if items:
                items_by_category[category.value] = len(items)
        
        return {
            "list_id": list_id,
            "name": shopping_list.name,
            "total_items": len(shopping_list.items),
            "checked_items": sum(1 for item in shopping_list.items if item.checked),
            "unchecked_items": sum(1 for item in shopping_list.items if not item.checked),
            "items_by_category": items_by_category,
            "created_at": shopping_list.created_at.isoformat(),
            "updated_at": shopping_list.updated_at.isoformat()
        }
