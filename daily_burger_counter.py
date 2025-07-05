"""
Daily Burger Counter System
Counts burger orders from Square API for daily and yearly tracking
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from square_client import SquareClientManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DailyBurgerCounter:
    """Handles daily burger counting from Square orders"""
    
    def __init__(self):
        self.square_client = SquareClientManager()
        
    def count_todays_burgers(self) -> Dict[str, Any]:
        """Count all burger orders from today"""
        try:
            # Get today's date range
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time())
            end_time = datetime.combine(today, datetime.max.time())
            
            logger.info(f"🍔 Counting burgers for {today}")
            
            # Get all orders from today
            orders = self._get_orders_for_date_range(start_time, end_time)
            
            # Count burger items
            burger_count = 0
            burger_orders = []
            
            for order in orders:
                order_burgers = self._count_burgers_in_order(order)
                if order_burgers > 0:
                    burger_count += order_burgers
                    burger_orders.append({
                        'order_id': order.get('id'),
                        'burger_count': order_burgers,
                        'created_at': order.get('created_at')
                    })
            
            result = {
                'date': today.isoformat(),
                'burger_count': burger_count,
                'total_orders': len(orders),
                'burger_orders': burger_orders,
                'counted_at': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Today's burger count: {burger_count} burgers from {len(burger_orders)} orders")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error counting today's burgers: {e}")
            return {
                'date': datetime.now().date().isoformat(),
                'burger_count': 0,
                'error': str(e),
                'counted_at': datetime.now().isoformat()
            }
    
    def _get_orders_for_date_range(self, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
        """Get all orders from Square for a specific date range"""
        try:
            # Format times for Square API
            start_str = start_time.isoformat() + "Z"
            end_str = end_time.isoformat() + "Z"
            
            # Get orders from Square API
            orders = self.square_client.get_orders_by_date_range(start_str, end_str)
            
            logger.debug(f"Retrieved {len(orders)} orders from {start_time.date()}")
            return orders
            
        except Exception as e:
            logger.error(f"Error getting orders for date range: {e}")
            return []
    
    def _count_burgers_in_order(self, order: Dict[str, Any]) -> int:
        """Count burger items in a single order"""
        burger_count = 0
        
        try:
            line_items = order.get('line_items', [])
            
            for item in line_items:
                if self._is_burger_item(item):
                    quantity = int(item.get('quantity', '1'))
                    burger_count += quantity
                    logger.debug(f"Found {quantity} burger(s): {item.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error counting burgers in order {order.get('id')}: {e}")
        
        return burger_count
    
    def _is_burger_item(self, line_item: Dict[str, Any]) -> bool:
        """Check if a line item is a burger"""
        try:
            # Check if item has a category
            catalog_object_id = line_item.get('catalog_object_id')
            if catalog_object_id:
                return self.square_client._is_burger_category_item(catalog_object_id)
            
            # Fallback: check item name for burger keywords
            item_name = line_item.get('name', '').lower()
            burger_keywords = ['burger', 'patty', 'smash']
            
            return any(keyword in item_name for keyword in burger_keywords)
            
        except Exception as e:
            logger.error(f"Error checking if item is burger: {e}")
            return False