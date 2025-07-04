import os
import logging
import time
import threading
import json
from github import Github
from git import Repo
from webhook_handler import WebhookHandler
from counter_manager import CounterManager
from daily_service import DailyBurgerService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize managers
webhook_handler = WebhookHandler()
counter_manager = CounterManager()
daily_service = DailyBurgerService()

# Open existing repository
repo = Repo('/home/pi/Desktop/charlabeast.github.io')

#current_count = counter_manager.get_counter()

#DESIGN
def RUN():
    #current_count = counter_manager.get_counter()
    logger.info("Burger Count Refresh")
    current_count = counter_manager.get_counter()
    yearly_result = daily_service.count_yearly_burgers()

    if yearly_result['number'] != current_count:
        counter_manager.write_counter_file(yearly_result)
        # Add files
        repo.index.add(['counter.json'])
        # Commit changes
        repo.index.commit('Update!')
        # Push to remote
        origin = repo.remote(name='origin')
        origin.push()
    threading.Timer(15, RUN).start()

RUN()
