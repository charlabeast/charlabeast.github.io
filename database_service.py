import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from models import ProcessedOrder, BurgerSalesCounter, BurgerItem, db
import json

logger = logging.getLogger(__name__)

class DatabaseBurgerService:
    """Service to manage burger counting with database tracking"""
    
    def __init__(self):
        self.current_year = 2025
    
    def get_total_burger_count(self) -> int:
        """Get the current total burger count from database"""
        counter = BurgerSalesCounter.query.filter_by(year=self.current_year).first()
        if counter:
            return counter.total_count
        return 0
    
    def is_order_processed(self, order_id: str) -> bool:
        """Check if an order has already been processed"""
        return ProcessedOrder.query.filter_by(square_order_id=order_id).first() is not None
    
    def process_new_order(self, order_data: Dict[str, Any], square_client) -> int:
        """Process a new order and return burger count added"""
        order_id = order_data.get('id')
        if not order_id:
            return 0
        
        # Check if already processed
        if self.is_order_processed(order_id):
            logger.info(f"Order {order_id} already processed, skipping")
            return 0
        
        # Count burgers in this order
        line_items = order_data.get('line_items', [])
        burger_count = 0
        burger_items = []
        
        for item in line_items:
            if square_client._is_burger_item(item):
                quantity = int(item.get('quantity', 1))
                burger_count += quantity
                
                # Record this burger item
                burger_item = BurgerItem(
                    square_order_id=order_id,
                    item_name=item.get('name', 'Unknown'),
                    quantity=quantity
                )
                burger_items.append(burger_item)
                logger.info(f"Found burger: {item.get('name')} x{quantity}")
        
        # Save processed order
        processed_order = ProcessedOrder(
            square_order_id=order_id,
            burger_count=burger_count,
            order_data=json.dumps(order_data, default=str)
        )
        
        try:
            # Add to database
            db.session.add(processed_order)
            for burger_item in burger_items:
                db.session.add(burger_item)
            
            # Update total counter
            self._update_total_count(burger_count)
            
            db.session.commit()
            logger.info(f"Processed order {order_id}: +{burger_count} burgers")
            return burger_count
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing order {order_id}: {e}")
            return 0
    
    def _update_total_count(self, additional_count: int):
        """Update the total burger count"""
        counter = BurgerSalesCounter.query.filter_by(year=self.current_year).first()
        
        if not counter:
            # Create new counter
            counter = BurgerSalesCounter(
                total_count=additional_count,
                year=self.current_year
            )
            db.session.add(counter)
        else:
            # Update existing counter
            counter.total_count += additional_count
            counter.last_updated = datetime.utcnow()
    
    def reset_and_reprocess_all_orders(self, orders: List[Dict[str, Any]], square_client) -> int:
        """Reset database and reprocess all orders for accuracy"""
        try:
            # Clear existing data
            ProcessedOrder.query.filter_by().delete()
            BurgerItem.query.filter_by().delete()
            BurgerSalesCounter.query.filter_by(year=self.current_year).delete()
            
            total_burgers = 0
            processed_orders = 0
            
            logger.info(f"Reprocessing {len(orders)} orders...")
            
            # Process each order
            for order in orders:
                burger_count = self.process_new_order(order, square_client)
                total_burgers += burger_count
                if burger_count > 0:
                    processed_orders += 1
            
            logger.info(f"Reset complete: {total_burgers} total burgers from {processed_orders} orders")
            return total_burgers
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error during reset and reprocess: {e}")
            return 0
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about processed orders"""
        total_orders = ProcessedOrder.query.count()
        total_items = BurgerItem.query.count()
        total_burgers = self.get_total_burger_count()
        
        return {
            'total_orders_processed': total_orders,
            'total_burger_items': total_items,
            'total_burger_count': total_burgers,
            'last_updated': BurgerSalesCounter.query.filter_by(year=self.current_year).first().last_updated if BurgerSalesCounter.query.filter_by(year=self.current_year).first() else None
        }