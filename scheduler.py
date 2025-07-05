"""
Automatic Daily Rollup Scheduler
Runs at 3am daily to add previous day's burger count to yearly total
"""

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from daily_service import DailyBurgerService

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class BurgerScheduler:
    """Handles automatic daily rollup scheduling"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.daily_service = DailyBurgerService()
        self.current_base = 1501  # Current base total (1296 + 205 from May 23rd)
        
    def start_scheduler(self):
        """Start the automatic scheduler"""
        try:
            # Schedule daily rollup at 11:41 PM Eastern Time (4:41 AM UTC next day)
            self.scheduler.add_job(
                func=self.perform_daily_rollup,
                trigger=CronTrigger(hour=4, minute=41),
                id='daily_burger_rollup',
                name='Daily Burger Count Rollup',
                replace_existing=True
            )
            
            self.scheduler.start()
            logger.info("🕒 Burger rollup scheduler started - will run daily at 11:41 PM Eastern Time")
            
        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}")
    
    def perform_daily_rollup(self):
        """Perform the daily rollup at 3am"""
        try:
            yesterday = datetime.now().date() - timedelta(days=1)
            logger.info(f"🍔 Starting 3AM rollup for {yesterday}")
            
            # Get yesterday's burger count from Square
            yesterday_count = self._get_yesterday_burger_count(yesterday)
            
            if yesterday_count > 0:
                # Update the base total
                self.current_base += yesterday_count
                
                # Update the code with new base total
                self._update_base_total_in_code(self.current_base)
                
                logger.info(f"✅ 3AM Rollup complete: Added {yesterday_count} burgers. New base total: {self.current_base}")
            else:
                logger.info(f"📊 No burgers to add from {yesterday}")
                
        except Exception as e:
            logger.error(f"❌ Error in 3AM rollup: {e}")
    
    def _get_yesterday_burger_count(self, target_date):
        """Get burger count for yesterday"""
        try:
            # Calculate yesterday's date range
            start_time = datetime.combine(target_date, datetime.min.time())
            end_time = datetime.combine(target_date, datetime.max.time())
            
            # Format for Square API
            start_str = start_time.isoformat() + "Z"
            end_str = end_time.isoformat() + "Z"
            
            # Get orders from Square
            orders = self.daily_service.square_client.get_orders_by_date_range(start_str, end_str)
            
            # Count burgers
            burger_count = 0
            for order in orders:
                burger_count += self.daily_service._count_burgers_in_order(order)
            
            logger.info(f"Found {burger_count} burgers for {target_date}")
            return burger_count
            
        except Exception as e:
            logger.error(f"Error getting yesterday's burger count: {e}")
            return 0
    
    def _update_base_total_in_code(self, new_base):
        """Update the base total - now uses counter.json instead of modifying code"""
        try:
            # Update the counter file directly instead of modifying code
            from counter_manager import CounterManager
            counter_manager = CounterManager()
            counter_manager.set_counter(new_base)
            logger.info(f"✅ Updated base counter to {new_base}")
            
        except Exception as e:
            logger.error(f"Error updating base total: {e}")
    
    def _get_last_added(self):
        """Get the last burger count that was added"""
        # This is a simplified approach - in practice you'd track this better
        return 0
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

# Global scheduler instance
burger_scheduler = BurgerScheduler()