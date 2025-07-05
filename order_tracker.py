import json
import os
from datetime import datetime
from threading import Lock
import logging

logger = logging.getLogger(__name__)

class OrderTracker:
    """Simple file-based order tracking to prevent double counting"""
    
    def __init__(self, tracker_file: str = "data/processed_orders.json"):
        self.tracker_file = tracker_file
        self.lock = Lock()
        self._ensure_tracker_file()
    
    def _ensure_tracker_file(self):
        """Ensure the tracker file exists"""
        os.makedirs(os.path.dirname(self.tracker_file), exist_ok=True)
        if not os.path.exists(self.tracker_file):
            with open(self.tracker_file, 'w') as f:
                json.dump({"processed_orders": [], "last_updated": datetime.now().isoformat()}, f)
    
    def is_order_processed(self, order_id: str) -> bool:
        """Check if an order has already been processed"""
        with self.lock:
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                return order_id in data.get("processed_orders", [])
            except Exception as e:
                logger.error(f"Error checking processed order: {e}")
                return False
    
    def mark_order_processed(self, order_id: str, burger_count: int = 0):
        """Mark an order as processed"""
        with self.lock:
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                
                processed_orders = data.get("processed_orders", [])
                if order_id not in processed_orders:
                    processed_orders.append(order_id)
                    data["processed_orders"] = processed_orders
                    data["last_updated"] = datetime.now().isoformat()
                    data["total_processed"] = len(processed_orders)
                    
                    with open(self.tracker_file, 'w') as f:
                        json.dump(data, f, indent=2)
                    
                    logger.info(f"Marked order {order_id} as processed (+{burger_count} burgers)")
                    return True
                
            except Exception as e:
                logger.error(f"Error marking order as processed: {e}")
                return False
        
        return False
    
    def get_stats(self) -> dict:
        """Get statistics about processed orders"""
        with self.lock:
            try:
                with open(self.tracker_file, 'r') as f:
                    data = json.load(f)
                
                return {
                    "total_processed_orders": len(data.get("processed_orders", [])),
                    "last_updated": data.get("last_updated", "Never")
                }
                
            except Exception as e:
                logger.error(f"Error getting tracker stats: {e}")
                return {"total_processed_orders": 0, "last_updated": "Error"}