import os
import logging
import requests
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

class SquareClientManager:
    def __init__(self):
        # Get Square credentials from environment
        self.access_token = "EAAAlhJMyWPaslffhdKWs03uHpUkmzR3geyBCzIqNFIP6lKeAhAbtz0PHrnZyaBV"
        self.application_id = "sq0idp-nRqUMKbj3r5QEa16NXIwLg"
        self.environment = "production"  # sandbox or production
        
        if not self.access_token:
            logger.warning("SQUARE_ACCESS_TOKEN not set - Square API calls will fail")
        
        # Set base URL based on environment
        if self.environment.lower() == 'production':
            self.base_url = 'https://connect.squareup.com'
        
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
            'Square-Version': '2023-10-18'
        }
        
        logger.info(f"Square client initialized for {self.environment} environment")
    
    def _make_request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make HTTP request to Square API"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == 'GET':
                response = requests.get(url, headers=self.headers, params=data or {})
            elif method.upper() == 'POST':
                response = requests.post(url, headers=self.headers, json=data or {})
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
            
            logger.debug(f"Square API Response Status: {response.status_code}")
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Square API HTTP error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response content: {e.response.text}")
                try:
                    error_data = e.response.json()
                    logger.error(f"Square API error details: {error_data}")
                except:
                    pass
            return {}
        except requests.exceptions.RequestException as e:
            logger.error(f"Square API request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
            return {}
    
    def check_order_for_burgers(self, order_id: str) -> bool:
        """Check if an order contains burger items"""
        if not self.access_token:
            logger.error("Square access token not available")
            return False
        
        try:
            # Get order details
            endpoint = f"/v2/orders/{order_id}"
            result = self._make_request('GET', endpoint)
            
            if not result:
                logger.error(f"Error retrieving order {order_id}")
                return False
            
            order = result.get('order', {})
            line_items = order.get('line_items', [])
            
            # Check each line item for burger category
            for item in line_items:
                if self._is_burger_item(item):
                    logger.info(f"Found burger item in order {order_id}")
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking order for burgers: {e}")
            return False
    
    def is_burger_item(self, line_item: Dict[str, Any]) -> bool:
        """Check if a line item is from the Burgers category"""
        try:
            # Check by name first - this is faster and more reliable
            item_name = line_item.get('name', '').lower()
            
            # Only count actual burger items - be very specific
            # Based on your actual menu items we've seen
            actual_burger_items = [
                #'the classic double'
                #'the retro double',
                #'kids burger',
                # 'simple burger',
                #'the simple double',
                # 'cheeseburger',
                # 'hamburger',
                'the works',
                'burger',
                'double',
                'patty'
                #'bend burger',
                #'the bacon avocado double',
                #'butter burger',
                #'wisconsin butter burger'
            ]
            
            # Check if this is actually a burger item
            for burger_item in actual_burger_items:
                if burger_item in item_name:
                    return True
                elif item_name.__contains__('fries'):
                    return False
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking if item is burger: {e}")
            return False
    
    def _is_burger_category(self, category_id: str) -> bool:
        """Check if a category ID corresponds to the Burgers category"""
        if not category_id:
            return False
        
        try:
            endpoint = f"/v2/catalog/object/{category_id}"
            result = self._make_request('GET', endpoint)
            
            if not result:
                return False
            
            category_object = result.get('object', {})
            category_data = category_object.get('category_data', {})
            category_name = category_data.get('name', '').lower()
            
            return 'burger' in category_name
            
        except Exception as e:
            logger.error(f"Error checking category: {e}")
            return False
    
    def get_burger_sales_count(self) -> int:
        """Get total count of burger sales from Square API"""
        if not self.access_token:
            logger.error("Square access token not available")
            return 0
        
        try:
            # Search for orders from entire 2025 year (increase limit to capture more data)
            recent_orders = self.get_recent_orders(limit=1000)
            burger_count = 0
            burger_orders = 0
            
            logger.info(f"Processing {len(recent_orders)} recent orders...")
            
            for order in recent_orders:
                line_items = order.get('line_items', [])
                order_has_burgers = False
                
                for item in line_items:
                    if self._is_burger_item(item):
                        # Count the quantity of burger items
                        quantity = int(item.get('quantity', 1))
                        burger_count += quantity
                        order_has_burgers = True
                
                if order_has_burgers:
                    burger_orders += 1
            
            logger.info(f"Found {burger_count} total burger sales from {burger_orders} orders")
            return burger_count
            
        except Exception as e:
            logger.error(f"Error getting burger sales count: {e}")
            return 0
    
    def get_locations(self) -> List[Dict[str, Any]]:
        """Get all locations for this Square account"""
        if not self.access_token:
            logger.error("No access token available")
            return []
        
        try:
            endpoint = "/v2/locations"
            logger.info(f"Fetching locations from: {self.base_url}{endpoint}")
            result = self._make_request('GET', endpoint)
            
            if not result:
                logger.error("Empty result when getting locations")
                return []
            
            locations = result.get('locations', [])
            logger.info(f"Found {len(locations)} locations")
            
            # Log location details for debugging
            for i, loc in enumerate(locations):
                logger.info(f"Location {i+1}: {loc.get('name', 'Unknown')} (ID: {loc.get('id', 'No ID')})")
            
            return locations
            
        except Exception as e:
            logger.error(f"Error getting locations: {e}", exc_info=True)
            return []

    def get_recent_orders(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent orders (for debugging/testing)"""
        if not self.access_token:
            return []
        
        try:
            # First get all locations
            locations = self.get_locations()
            if not locations:
                logger.error("No locations found - cannot search orders")
                return []
            
            # Use all location IDs
            location_ids = [loc.get('id') for loc in locations if loc.get('id')]
            
            # Search for orders from January 1st, 2025 to now
            from datetime import datetime
            start_time = datetime(2025, 1, 1).isoformat() + 'Z'
            
            search_query = {
                'filter': {
                    'date_time_filter': {
                        'created_at': {
                            'start_at': start_time
                        }
                    }
                },
                'sort': {
                    'sort_field': 'CREATED_AT',
                    'sort_order': 'DESC'
                }
            }
            
            endpoint = "/v2/orders/search"
            data = {
                'location_ids': location_ids,
                'query': search_query,
                'limit': limit
            }
            
            result = self._make_request('POST', endpoint, data)
            
            if not result:
                logger.error("Error searching orders")
                return []
            
            return result.get('orders', [])
            
        except Exception as e:
            logger.error(f"Error getting recent orders: {e}")
            return []

    def get_orders_by_date_range(self, start_time: str, end_time: str, limit: int = 1000) -> List[Dict[str, Any]]:
        """Get orders within a specific date range"""
        if not self.access_token:
            return []
        
        try:
            # First get all locations
            locations = self.get_locations()
            if not locations:
                logger.error("No locations found - cannot search orders")
                return []
            
            # Use all location IDs
            location_ids = [loc.get('id') for loc in locations if loc.get('id')]
            
            search_query = {
                'filter': {
                    'date_time_filter': {
                        'created_at': {
                            'start_at': start_time,
                            'end_at': end_time
                        }
                    }
                },
                'sort': {
                    'sort_field': 'CREATED_AT',
                    'sort_order': 'DESC'
                }
            }
            
            endpoint = "/v2/orders/search"
            all_orders = []
            cursor = None
            page_count = 0
            
            # Paginate through all results
            while True:
                page_count += 1
                
                data = {
                    'location_ids': location_ids,
                    'query': search_query,
                    'limit': min(limit, 1000)  # Square API max is 1000 per request
                }
                
                # Add cursor for pagination (except first request)
                if cursor:
                    data['cursor'] = cursor
                
                logger.info(f"Fetching page {page_count} of orders...")
                logger.debug(f"Request data: {data}")
                result = self._make_request('POST', endpoint, data)
                
                if not result:
                    logger.error(f"Error on page {page_count} - stopping pagination")
                    logger.error(f"Failed request data was: {data}")
                    break
                
                page_orders = result.get('orders', [])
                all_orders.extend(page_orders)
                
                logger.info(f"Page {page_count}: Found {len(page_orders)} orders (total so far: {len(all_orders)})")
                
                # Check if there are more pages
                cursor = result.get('cursor')
                if not cursor or len(page_orders) == 0:
                    logger.info(f"No more pages - completed pagination after {page_count} pages")
                    break
                
                # Safety check to prevent infinite loops
                if page_count > 100:  # Adjust based on your expected data size
                    logger.warning(f"Reached maximum page limit ({page_count}) - stopping pagination")
                    break
            
            logger.info(f"Found {len(all_orders)} orders between {start_time} and {end_time}")
            return all_orders
            
        except Exception as e:
            logger.error(f"Error getting orders by date range: {e}")
            return []

    def _is_burger_category_item(self, catalog_object_id: str) -> bool:
        """Check if a catalog item is from the burger category"""
        try:
            response = self._make_request("GET", f"/v2/catalog/object/{catalog_object_id}")
            catalog_object = response.get('object', {})
            
            # Check if this item has a category
            item_data = catalog_object.get('item_data', {})
            category_id = item_data.get('category_id')
            
            if category_id:
                return self._is_burger_category(category_id)
            
            # Fallback: check item name
            item_name = item_data.get('name', '').lower()
            return 'burger' in item_name or 'patty' in item_name
            
        except Exception as e:
            logger.error(f"Error checking catalog item {catalog_object_id}: {e}")
            return False
