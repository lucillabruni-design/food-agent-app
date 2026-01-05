"""
ODA Supermarket API Integration Module

This module provides integration with the ODA supermarket API for:
- Product search and catalog browsing
- Shopping list management
- Price comparison and monitoring
- Availability tracking
"""

import logging
import requests
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class ProductCategory(Enum):
    """Available product categories in ODA"""
    FRUITS_VEGETABLES = "fruits_vegetables"
    DAIRY_EGGS = "dairy_eggs"
    MEAT_SEAFOOD = "meat_seafood"
    BAKERY = "bakery"
    PANTRY = "pantry"
    FROZEN = "frozen"
    BEVERAGES = "beverages"
    SNACKS = "snacks"
    ORGANIC = "organic"
    HEALTH_BEAUTY = "health_beauty"


class SortOrder(Enum):
    """Sorting options for product search"""
    PRICE_LOW_TO_HIGH = "price_asc"
    PRICE_HIGH_TO_LOW = "price_desc"
    POPULARITY = "popularity"
    RELEVANCE = "relevance"
    NEWEST = "newest"
    DISCOUNT = "discount"


@dataclass
class Product:
    """Represents a product from ODA"""
    id: str
    name: str
    price: float
    currency: str = "NOK"
    original_price: Optional[float] = None
    discount_percentage: Optional[float] = None
    category: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    availability: bool = True
    stock_quantity: Optional[int] = None
    unit: Optional[str] = None
    sku: Optional[str] = None
    barcode: Optional[str] = None
    brand: Optional[str] = None
    allergens: Optional[List[str]] = None
    nutritional_info: Optional[Dict] = None
    
    def get_discount_amount(self) -> float:
        """Calculate absolute discount amount"""
        if self.original_price and self.price < self.original_price:
            return self.original_price - self.price
        return 0.0
    
    def is_on_sale(self) -> bool:
        """Check if product is on sale"""
        return self.original_price is not None and self.original_price > self.price
    
    def to_dict(self) -> Dict:
        """Convert product to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'currency': self.currency,
            'original_price': self.original_price,
            'discount_percentage': self.discount_percentage,
            'category': self.category,
            'description': self.description,
            'image_url': self.image_url,
            'availability': self.availability,
            'stock_quantity': self.stock_quantity,
            'unit': self.unit,
            'sku': self.sku,
            'barcode': self.barcode,
            'brand': self.brand,
            'allergens': self.allergens,
            'nutritional_info': self.nutritional_info,
        }


@dataclass
class ShoppingListItem:
    """Represents an item in a shopping list"""
    product: Product
    quantity: float
    unit: str
    notes: Optional[str] = None
    completed: bool = False
    added_date: Optional[datetime] = None
    
    def get_total_price(self) -> float:
        """Calculate total price for this item"""
        return self.product.price * self.quantity
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'product': self.product.to_dict(),
            'quantity': self.quantity,
            'unit': self.unit,
            'notes': self.notes,
            'completed': self.completed,
            'added_date': self.added_date.isoformat() if self.added_date else None,
            'total_price': self.get_total_price(),
        }


@dataclass
class PriceComparison:
    """Represents price comparison data"""
    product_id: str
    product_name: str
    oda_price: float
    competitor_prices: Dict[str, float]  # {competitor_name: price}
    lowest_price: float
    lowest_price_at: str  # competitor name or 'ODA'
    price_difference: float
    savings: float
    last_updated: datetime
    
    def get_best_option(self) -> Tuple[str, float]:
        """Get the cheapest option"""
        options = {'ODA': self.oda_price, **self.competitor_prices}
        best_option = min(options.items(), key=lambda x: x[1])
        return best_option
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'product_id': self.product_id,
            'product_name': self.product_name,
            'oda_price': self.oda_price,
            'competitor_prices': self.competitor_prices,
            'lowest_price': self.lowest_price,
            'lowest_price_at': self.lowest_price_at,
            'price_difference': self.price_difference,
            'savings': self.savings,
            'last_updated': self.last_updated.isoformat(),
        }


class ODAIntegration:
    """Main class for ODA supermarket API integration"""
    
    BASE_URL = "https://api.oda.com/v1"
    DEFAULT_TIMEOUT = 10
    CACHE_DURATION = timedelta(hours=1)
    
    def __init__(self, api_key: str, store_id: Optional[str] = None):
        """
        Initialize ODA integration
        
        Args:
            api_key: ODA API key for authentication
            store_id: Optional store ID for location-specific queries
        """
        self.api_key = api_key
        self.store_id = store_id
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
        })
        self._cache = {}
        self._cache_timestamps = {}
        logger.info(f"ODA Integration initialized with store_id: {store_id}")
    
    def _get_cache_key(self, *args) -> str:
        """Generate cache key from arguments"""
        key_string = '|'.join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self._cache_timestamps:
            return False
        elapsed = datetime.now() - self._cache_timestamps[cache_key]
        return elapsed < self.CACHE_DURATION
    
    def _set_cache(self, cache_key: str, data: any) -> None:
        """Set cache with timestamp"""
        self._cache[cache_key] = data
        self._cache_timestamps[cache_key] = datetime.now()
    
    def _get_cache(self, cache_key: str) -> Optional[any]:
        """Get cached data if valid"""
        if self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        return None
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make HTTP request to ODA API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            Response JSON data
        """
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.DEFAULT_TIMEOUT,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"ODA API request failed: {str(e)}")
            raise
    
    def search_products(
        self,
        query: str,
        category: Optional[ProductCategory] = None,
        sort_by: SortOrder = SortOrder.RELEVANCE,
        limit: int = 20,
        offset: int = 0,
        in_stock_only: bool = True,
    ) -> List[Product]:
        """
        Search for products in ODA catalog
        
        Args:
            query: Search query string
            category: Optional category filter
            sort_by: Sorting order
            limit: Maximum number of results
            offset: Pagination offset
            in_stock_only: Only return in-stock items
            
        Returns:
            List of Product objects
        """
        cache_key = self._get_cache_key('search', query, category, sort_by, limit, offset)
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        params = {
            'q': query,
            'limit': limit,
            'offset': offset,
            'sort': sort_by.value,
        }
        
        if category:
            params['category'] = category.value
        
        if in_stock_only:
            params['in_stock'] = 'true'
        
        try:
            response = self._make_request('GET', '/products/search', params=params)
            products = [self._parse_product(item) for item in response.get('results', [])]
            self._set_cache(cache_key, products)
            logger.info(f"Found {len(products)} products for query: {query}")
            return products
        except Exception as e:
            logger.error(f"Product search failed: {str(e)}")
            return []
    
    def get_product_details(self, product_id: str) -> Optional[Product]:
        """
        Get detailed information about a specific product
        
        Args:
            product_id: ODA product ID
            
        Returns:
            Product object or None if not found
        """
        cache_key = self._get_cache_key('product_details', product_id)
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            response = self._make_request('GET', f'/products/{product_id}')
            product = self._parse_product(response)
            self._set_cache(cache_key, product)
            return product
        except Exception as e:
            logger.error(f"Failed to get product details for {product_id}: {str(e)}")
            return None
    
    def browse_category(
        self,
        category: ProductCategory,
        limit: int = 50,
        offset: int = 0,
        sort_by: SortOrder = SortOrder.POPULARITY,
    ) -> List[Product]:
        """
        Browse products in a specific category
        
        Args:
            category: Product category
            limit: Maximum results
            offset: Pagination offset
            sort_by: Sorting order
            
        Returns:
            List of Product objects
        """
        cache_key = self._get_cache_key('category', category.value, limit, offset, sort_by)
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        params = {
            'category': category.value,
            'limit': limit,
            'offset': offset,
            'sort': sort_by.value,
        }
        
        try:
            response = self._make_request('GET', '/products/categories', params=params)
            products = [self._parse_product(item) for item in response.get('items', [])]
            self._set_cache(cache_key, products)
            logger.info(f"Retrieved {len(products)} products from category: {category.value}")
            return products
        except Exception as e:
            logger.error(f"Category browse failed: {str(e)}")
            return []
    
    def get_on_sale_products(self, limit: int = 30) -> List[Product]:
        """
        Get products currently on sale
        
        Args:
            limit: Maximum results
            
        Returns:
            List of discounted Product objects
        """
        cache_key = self._get_cache_key('on_sale', limit)
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        params = {'limit': limit, 'discount': 'true'}
        
        try:
            response = self._make_request('GET', '/products/discounts', params=params)
            products = [self._parse_product(item) for item in response.get('items', [])]
            self._set_cache(cache_key, products)
            logger.info(f"Retrieved {len(products)} products on sale")
            return products
        except Exception as e:
            logger.error(f"Failed to get sale products: {str(e)}")
            return []
    
    def create_shopping_list(self, name: str, items: Optional[List[Dict]] = None) -> Dict:
        """
        Create a new shopping list
        
        Args:
            name: Name for the shopping list
            items: Optional list of items to add
            
        Returns:
            Created shopping list data
        """
        payload = {
            'name': name,
            'items': items or [],
        }
        
        try:
            response = self._make_request('POST', '/shopping-lists', json=payload)
            logger.info(f"Created shopping list: {name}")
            return response
        except Exception as e:
            logger.error(f"Failed to create shopping list: {str(e)}")
            raise
    
    def add_to_shopping_list(
        self,
        list_id: str,
        product_id: str,
        quantity: float,
        unit: str = 'unit',
    ) -> Dict:
        """
        Add item to shopping list
        
        Args:
            list_id: Shopping list ID
            product_id: Product ID to add
            quantity: Quantity to add
            unit: Unit of measurement
            
        Returns:
            Updated shopping list item
        """
        payload = {
            'product_id': product_id,
            'quantity': quantity,
            'unit': unit,
        }
        
        try:
            response = self._make_request(
                'POST',
                f'/shopping-lists/{list_id}/items',
                json=payload
            )
            logger.info(f"Added product {product_id} to shopping list {list_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to add item to shopping list: {str(e)}")
            raise
    
    def remove_from_shopping_list(self, list_id: str, item_id: str) -> bool:
        """
        Remove item from shopping list
        
        Args:
            list_id: Shopping list ID
            item_id: Item ID to remove
            
        Returns:
            Success status
        """
        try:
            self._make_request('DELETE', f'/shopping-lists/{list_id}/items/{item_id}')
            logger.info(f"Removed item {item_id} from shopping list {list_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to remove item from shopping list: {str(e)}")
            return False
    
    def get_shopping_list(self, list_id: str) -> Optional[Dict]:
        """
        Get shopping list details
        
        Args:
            list_id: Shopping list ID
            
        Returns:
            Shopping list data or None
        """
        try:
            response = self._make_request('GET', f'/shopping-lists/{list_id}')
            return response
        except Exception as e:
            logger.error(f"Failed to get shopping list: {str(e)}")
            return None
    
    def calculate_shopping_list_total(self, list_id: str) -> Optional[float]:
        """
        Calculate total price for shopping list
        
        Args:
            list_id: Shopping list ID
            
        Returns:
            Total price or None
        """
        shopping_list = self.get_shopping_list(list_id)
        if not shopping_list:
            return None
        
        total = 0.0
        for item in shopping_list.get('items', []):
            total += float(item.get('price', 0)) * float(item.get('quantity', 1))
        
        return total
    
    def compare_prices(
        self,
        product_id: str,
        competitors: Optional[Dict[str, str]] = None,
    ) -> Optional[PriceComparison]:
        """
        Compare ODA price with competitors
        
        Args:
            product_id: ODA product ID
            competitors: Dict of {competitor_name: product_url}
            
        Returns:
            PriceComparison object or None
        """
        product = self.get_product_details(product_id)
        if not product:
            return None
        
        competitor_prices = {}
        if competitors:
            for competitor_name, competitor_url in competitors.items():
                try:
                    # This is a placeholder for actual competitor API calls
                    # Implementation would depend on specific competitor APIs
                    competitor_prices[competitor_name] = self._fetch_competitor_price(
                        competitor_url
                    )
                except Exception as e:
                    logger.warning(f"Failed to get {competitor_name} price: {str(e)}")
        
        all_prices = {'ODA': product.price, **competitor_prices}
        lowest_price = min(all_prices.values())
        lowest_at = min(all_prices, key=all_prices.get)
        
        comparison = PriceComparison(
            product_id=product_id,
            product_name=product.name,
            oda_price=product.price,
            competitor_prices=competitor_prices,
            lowest_price=lowest_price,
            lowest_price_at=lowest_at,
            price_difference=product.price - lowest_price,
            savings=max(0, product.price - lowest_price),
            last_updated=datetime.now(),
        )
        
        logger.info(f"Price comparison for {product.name}: ODA {product.price} vs lowest {lowest_price}")
        return comparison
    
    def find_price_matches(
        self,
        target_price: float,
        category: Optional[ProductCategory] = None,
        tolerance: float = 0.5,
    ) -> List[Product]:
        """
        Find products within a price range
        
        Args:
            target_price: Target price to match
            category: Optional category filter
            tolerance: Price tolerance in percentage
            
        Returns:
            List of matching products
        """
        min_price = target_price * (1 - tolerance / 100)
        max_price = target_price * (1 + tolerance / 100)
        
        params = {
            'price_min': min_price,
            'price_max': max_price,
        }
        
        if category:
            params['category'] = category.value
        
        try:
            response = self._make_request('GET', '/products/price-range', params=params)
            products = [self._parse_product(item) for item in response.get('items', [])]
            logger.info(f"Found {len(products)} products in price range {min_price}-{max_price}")
            return products
        except Exception as e:
            logger.error(f"Failed to find price matches: {str(e)}")
            return []
    
    def get_weekly_offers(self) -> List[Product]:
        """
        Get this week's special offers
        
        Returns:
            List of offer products
        """
        cache_key = self._get_cache_key('weekly_offers')
        cached = self._get_cache(cache_key)
        if cached is not None:
            return cached
        
        try:
            response = self._make_request('GET', '/offers/weekly')
            products = [self._parse_product(item) for item in response.get('items', [])]
            self._set_cache(cache_key, products)
            logger.info(f"Retrieved {len(products)} weekly offers")
            return products
        except Exception as e:
            logger.error(f"Failed to get weekly offers: {str(e)}")
            return []
    
    def get_product_availability(self, product_id: str, store_id: Optional[str] = None) -> Dict:
        """
        Check product availability
        
        Args:
            product_id: Product ID
            store_id: Optional store ID (uses default if not specified)
            
        Returns:
            Availability data
        """
        store = store_id or self.store_id
        params = {}
        if store:
            params['store_id'] = store
        
        try:
            response = self._make_request(
                'GET',
                f'/products/{product_id}/availability',
                params=params
            )
            return response
        except Exception as e:
            logger.error(f"Failed to check availability: {str(e)}")
            return {}
    
    def _parse_product(self, data: Dict) -> Product:
        """Parse API response into Product object"""
        return Product(
            id=data.get('id', ''),
            name=data.get('name', ''),
            price=float(data.get('price', 0)),
            currency=data.get('currency', 'NOK'),
            original_price=float(data['original_price']) if data.get('original_price') else None,
            discount_percentage=float(data.get('discount', 0)) if data.get('discount') else None,
            category=data.get('category'),
            description=data.get('description'),
            image_url=data.get('image_url'),
            availability=data.get('available', True),
            stock_quantity=int(data['stock']) if data.get('stock') else None,
            unit=data.get('unit'),
            sku=data.get('sku'),
            barcode=data.get('barcode'),
            brand=data.get('brand'),
            allergens=data.get('allergens', []),
            nutritional_info=data.get('nutritional_info'),
        )
    
    def _fetch_competitor_price(self, url: str) -> float:
        """
        Placeholder for fetching competitor prices
        
        Args:
            url: Competitor product URL
            
        Returns:
            Price from competitor
        """
        # This is a placeholder implementation
        # Real implementation would parse specific competitor websites/APIs
        raise NotImplementedError("Competitor price fetching not implemented")
    
    def clear_cache(self) -> None:
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Cache cleared")
    
    def close(self) -> None:
        """Close session and cleanup"""
        self.session.close()
        logger.info("ODA Integration session closed")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Utility functions

def format_price(price: float, currency: str = "NOK") -> str:
    """Format price for display"""
    return f"{price:.2f} {currency}"


def calculate_savings(original_price: float, current_price: float) -> Dict[str, any]:
    """Calculate savings information"""
    if original_price <= current_price:
        return {
            'savings_amount': 0,
            'savings_percentage': 0,
            'is_discounted': False,
        }
    
    savings_amount = original_price - current_price
    savings_percentage = (savings_amount / original_price) * 100
    
    return {
        'savings_amount': round(savings_amount, 2),
        'savings_percentage': round(savings_percentage, 2),
        'is_discounted': True,
    }


def group_products_by_category(products: List[Product]) -> Dict[str, List[Product]]:
    """Group products by category"""
    grouped = {}
    for product in products:
        category = product.category or 'Uncategorized'
        if category not in grouped:
            grouped[category] = []
        grouped[category].append(product)
    return grouped


def filter_products_by_price(
    products: List[Product],
    min_price: float,
    max_price: float,
) -> List[Product]:
    """Filter products by price range"""
    return [p for p in products if min_price <= p.price <= max_price]


def sort_products_by_discount(products: List[Product], descending: bool = True) -> List[Product]:
    """Sort products by discount percentage"""
    return sorted(
        products,
        key=lambda p: p.discount_percentage or 0,
        reverse=descending
    )
