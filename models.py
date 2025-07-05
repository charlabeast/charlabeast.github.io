from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Date, Boolean

def init_models(db):
    """Initialize models with the db instance"""
    
    class ProcessedOrder(db.Model):
        """Track orders we've already processed to avoid double counting"""
    __tablename__ = 'processed_orders'
    
    id = Column(Integer, primary_key=True)
    square_order_id = Column(String(255), unique=True, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    burger_count = Column(Integer, default=0)
    order_data = Column(Text)  # Store order details for debugging
    
    def __repr__(self):
        return f'<ProcessedOrder {self.square_order_id}: {self.burger_count} burgers>'

class BurgerSalesCounter(db.Model):
    """Store the running total of burger sales"""
    __tablename__ = 'burger_sales_counter'
    
    id = Column(Integer, primary_key=True)
    total_count = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    year = Column(Integer, default=2025)
    
    def __repr__(self):
        return f'<BurgerSalesCounter {self.year}: {self.total_count} burgers>'

class BurgerItem(db.Model):
    """Track individual burger items for audit trail"""
    __tablename__ = 'burger_items'
    
    id = Column(Integer, primary_key=True)
    square_order_id = Column(String(255), nullable=False)
    item_name = Column(String(255), nullable=False)
    quantity = Column(Integer, default=1)
    processed_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<BurgerItem {self.item_name} x{self.quantity}>'

class DailyBurgerCount(db.Model):
    """Track daily burger counts before they're added to yearly total"""
    __tablename__ = 'daily_burger_counts'
    
    id = Column(Integer, primary_key=True)
    date = Column(Date, unique=True, nullable=False)
    burger_count = Column(Integer, default=0)
    total_orders = Column(Integer, default=0)
    counted_at = Column(DateTime, default=datetime.utcnow)
    added_to_yearly = Column(Boolean, default=False)
    
    def __repr__(self):
        return f'<DailyBurgerCount {self.date}: {self.burger_count} burgers>'

class YearlyBurgerTotal(db.Model):
    """Store the running yearly total of burger sales"""
    __tablename__ = 'yearly_burger_totals'
    
    id = Column(Integer, primary_key=True)
    year = Column(Integer, unique=True, nullable=False)
    total_burgers = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<YearlyBurgerTotal {self.year}: {self.total_burgers} burgers>'