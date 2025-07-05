"""
Simple Daily Burger Counting Service
Counts actual burger orders from Square API when webhooks trigger
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
from square_client import SquareClientManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class DailyBurgerService:
    """Handles daily burger counting from real Square orders"""
    
    def __init__(self):
        self.square_client = SquareClientManager()
        
    def count_todays_burgers(self) -> Dict[str, Any]:
        """Count all burger orders from today's real Square data"""
        try:
            # Get today's date range
            today = datetime.now().date()
            start_time = datetime.combine(today, datetime.min.time())
            end_time = datetime.combine(today, datetime.max.time())
            
            # Format for Square API
            start_str = start_time.isoformat() + "Z"
            end_str = end_time.isoformat() + "Z"
            
            logger.info(f"🍔 Counting burgers for {today}")
            
            # Get all orders from today using Square API
            orders = self.square_client.get_orders_by_date_range(start_str, end_str)
            
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
            
            logger.info(f"✅ Today's burger count: {burger_count} burgers from {len(burger_orders)} orders out of {len(orders)} total orders")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error counting today's burgers: {e}")
            return {
                'date': datetime.now().date().isoformat(),
                'burger_count': 0,
                'error': str(e),
                'counted_at': datetime.now().isoformat()
            }

    def count_yearly_burgers(self) -> Dict[str, Any]:
        """Count all burger orders from today's real Square data"""
        try:
            today = datetime.now().date()

            # Get yearly date range
            start_time = datetime.now().date().replace(month=1, day=1)
            end_time = datetime.now().date().replace(month=12, day=31)

            start_time = datetime.combine(start_time, datetime.min.time())
            end_time = datetime.combine(end_time, datetime.max.time())


            # Format for Square API
            start_str = start_time.isoformat() + "Z"
            end_str = end_time.isoformat() + "Z"

            logger.info(f"🍔 Counting burgers for this year so far!")

            # Get all orders from today using Square API
            orders = self.square_client.get_orders_by_date_range(start_str, end_str)

            #orders = list({v['id']: v for v in orders}.values())

            # Count burger items
            burger_count = 0
            burger_orders = []
            seen_order_ids = set()

            #
            # for order in orders:
            #     order_burgers = self._count_burgers_in_order(order)
            #     if order_burgers > 0:
            #         burger_count += order_burgers
            #         burger_orders.append({
            #             'order_id': order.get('id'),
            #             'burger_count': order_burgers,
            #             'created_at': order.get('created_at')
            #         })

            for order in orders:
                order_id = order.get('id')

                # Skip if we've already processed this order
                if order_id in seen_order_ids:
                    logger.debug(f"Skipping duplicate order: {order_id}")
                    continue

                seen_order_ids.add(order_id)
                order_burgers = self._count_burgers_in_order(order)

                if order_burgers > 0:
                    burger_count += order_burgers
                    burger_orders.append({
                        'order_id': order_id,
                        'burger_count': order_burgers,
                        'created_at': order.get('created_at')
                    })

            result = {
                #'date': today.isoformat(),
                'number': burger_count
                #'total_orders': len(orders),
                #'burger_orders': burger_orders,
                #'counted_at': datetime.now().isoformat()
            }

            logger.info(
                f"✅ This year's burger count: {burger_count} burgers from {len(burger_orders)} orders out of {len(orders)} total orders")
            return result

        except Exception as e:
            logger.error(f"❌ Error counting this year's burgers")
            return {
                'date': datetime.now().date().isoformat(),
                'burger_count': 0,
                'error': str(e),
                'counted_at': datetime.now().isoformat()
            }


    def _count_burgers_in_order(self, order: Dict[str, Any]) -> int:
        """Count burger items in a single order"""
        burger_count = 0
        
        try:
            line_items = order.get('line_items', [])
            state = order.get('state')

            
            for item in line_items:
                if self._is_burger_item(item):
                    quantity = int(item.get('quantity', '1'))
                    if (state == 'COMPLETED') | (state == 'OPEN'):
                        burger_count += quantity
                        #logger.debug(f"Found {quantity} burger(s): {item.get('name', 'Unknown')}")
            
        except Exception as e:
            logger.error(f"Error counting burgers in order {order.get('id')}: {e}")
        
        return burger_count
    
    def _is_burger_item(self, line_item: Dict[str, Any]) -> bool:
        """Check if a line item is a burger using your existing logic"""
        try:
            # Use the same burger detection logic from your Square client
            return self.square_client.is_burger_item(line_item)
            
        except Exception as e:
            logger.error(f"Error checking if item is burger: {e}")
            return False

