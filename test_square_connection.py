#!/usr/bin/env python3

import os
import requests
from square_client import SquareClientManager

def test_square_connection():
    """Test basic Square API connection"""
    print("Testing Square API connection...")
    
    # Initialize client
    client = SquareClientManager()
    
    # Test 1: Get locations
    print("\n1. Testing location access...")
    locations = client.get_locations()
    
    if locations:
        print(f"✓ Successfully found {len(locations)} locations:")
        for loc in locations:
            print(f"  - {loc.get('name', 'Unknown')} (ID: {loc.get('id', 'No ID')})")
    else:
        print("✗ No locations found or error occurred")
    
    # Test 2: Try to get recent orders (just a few)
    print("\n2. Testing order access...")
    try:
        orders = client.get_recent_orders(limit=5)
        if orders:
            print(f"✓ Successfully retrieved {len(orders)} recent orders")
            for i, order in enumerate(orders[:3]):
                print(f"  Order {i+1}: {order.get('id', 'No ID')} - {len(order.get('line_items', []))} items")
        else:
            print("✗ No orders found or error occurred")
    except Exception as e:
        print(f"✗ Error getting orders: {e}")
    
    # Test 3: Check burger counting
    print("\n3. Testing burger counting...")
    try:
        burger_count = client.get_burger_sales_count()
        print(f"✓ Burger count result: {burger_count}")
    except Exception as e:
        print(f"✗ Error counting burgers: {e}")

if __name__ == "__main__":
    test_square_connection()