#!/usr/bin/env python3

from square_client import SquareClientManager
from datetime import datetime
import json

def debug_orders():
    """Debug what items are actually in the orders"""
    square_client = SquareClientManager()
    
    # Get orders
    orders = square_client.get_recent_orders(limit=1000)
    
    print(f"=== ORDER DATE RANGE DEBUG ===")
    print(f"Total orders retrieved: {len(orders)}")
    
    if orders:
        # Get date range
        dates = []
        for order in orders:
            created_at = order.get('created_at', '')
            if created_at:
                # Parse the date
                try:
                    date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    dates.append(date_obj)
                except:
                    pass
        
        if dates:
            earliest = min(dates)
            latest = max(dates)
            print(f"Date range: {earliest.strftime('%Y-%m-%d')} to {latest.strftime('%Y-%m-%d')}")
            print(f"That's {(latest - earliest).days} days of data")
        
        # Count burger items by type
        burger_counts = {}
        total_burger_count = 0
        
        for order in orders:
            line_items = order.get('line_items', [])
            for item in line_items:
                if square_client._is_burger_item(item):
                    item_name = item.get('name', 'Unknown')
                    quantity = int(item.get('quantity', 1))
                    
                    if item_name in burger_counts:
                        burger_counts[item_name] += quantity
                    else:
                        burger_counts[item_name] = quantity
                    
                    total_burger_count += quantity
        
        print(f"\n=== DETAILED BURGER BREAKDOWN ===")
        for name, count in sorted(burger_counts.items()):
            print(f"{name}: {count}")
        
        print(f"\nTotal burgers found: {total_burger_count}")
    
    else:
        print("No orders retrieved!")

if __name__ == "__main__":
    debug_orders()