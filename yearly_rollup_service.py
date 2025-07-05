"""
3AM Daily Rollup Service
Adds daily burger counts to yearly total at 3am each day
"""

import os
import logging
from datetime import datetime, date
from typing import Dict, Any
from daily_service import DailyBurgerService
from counter_manager import CounterManager

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class YearlyRollupService:
    """Handles 3am daily rollup of burger counts to yearly total"""
    
    def __init__(self):
        self.daily_service = DailyBurgerService()
        self.counter_manager = CounterManager()
        # Your current yearly total through yesterday
        self.base_yearly_total = 1296
        
    def perform_daily_rollup(self, target_date: date = None) -> Dict[str, Any]:
        """Perform the 3am rollup for a specific date"""
        try:
            if target_date is None:
                target_date = datetime.now().date()
            
            logger.info(f"🕒 Performing 3AM rollup for {target_date}")
            
            # Get yesterday's burger count (since we run at 3am, we're rolling up yesterday)
            yesterday = target_date
            daily_count = self._get_daily_burger_count(yesterday)
            
            # Calculate new yearly total
            new_yearly_total = self.base_yearly_total + daily_count
            
            # Update the counter file with the new yearly total
            self.counter_manager.set_counter(new_yearly_total)
            
            # Store rollup info for tracking
            rollup_data = {
                'date': yesterday.isoformat(),
                'daily_burgers': daily_count,
                'previous_yearly_total': self.base_yearly_total,
                'new_yearly_total': new_yearly_total,
                'rollup_completed_at': datetime.now().isoformat()
            }
            
            # Update the base total for next time
            self.base_yearly_total = new_yearly_total
            
            logger.info(f"✅ 3AM Rollup complete: Added {daily_count} burgers. New yearly total: {new_yearly_total}")
            return rollup_data
            
        except Exception as e:
            logger.error(f"❌ Error in 3AM rollup: {e}")
            return {
                'error': str(e),
                'rollup_completed_at': datetime.now().isoformat()
            }
    
    def _get_daily_burger_count(self, target_date: date) -> int:
        """Get burger count for a specific date"""
        try:
            # If it's today, use the daily service to get real-time count
            if target_date == datetime.now().date():
                daily_result = self.daily_service.count_todays_burgers()
                return daily_result.get('burger_count', 0)
            else:
                # For past dates, we'd need to query Square API for that specific date
                # For now, return 0 for past dates since we're starting fresh
                return 0
                
        except Exception as e:
            logger.error(f"Error getting daily count for {target_date}: {e}")
            return 0
    
    def get_current_yearly_total(self) -> int:
        """Get the current yearly total"""
        return self.counter_manager.get_counter()
    
    def simulate_rollup(self) -> Dict[str, Any]:
        """Simulate what tonight's 3am rollup will do"""
        try:
            today = datetime.now().date()
            today_burgers = self.daily_service.count_todays_burgers()
            daily_count = today_burgers.get('burger_count', 0)
            
            projected_total = self.base_yearly_total + daily_count
            
            return {
                'current_date': today.isoformat(),
                'base_yearly_total': self.base_yearly_total,
                'todays_burgers': daily_count,
                'projected_yearly_total': projected_total,
                'will_rollup_at': '03:00 AM tomorrow'
            }
            
        except Exception as e:
            logger.error(f"Error simulating rollup: {e}")
            return {'error': str(e)}