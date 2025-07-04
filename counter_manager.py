import json
import os
import logging
from threading import Lock
from typing import Dict, Any

logger = logging.getLogger(__name__)

class CounterManager:
    def __init__(self, counter_file: str = "/home/pi/Desktop/charlabeast.github.io/counter.json"):
        self.counter_file = counter_file
        self.lock = Lock()
        #self._ensure_data_directory()
        #self._ensure_counter_file()
        #self._read_counter_file()
    
    def _ensure_data_directory(self):
        """Ensure the data directory exists"""
        data_dir = os.path.dirname(self.counter_file)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
            logger.info(f"Created data directory: {data_dir}")
    
    def _ensure_counter_file(self):
        """Ensure the counter file exists with initial value"""
        if not os.path.exists(self.counter_file):
            self._write_counter_file({"counter": 0})
            logger.info(f"Created initial counter file: {self.counter_file}")
    
    def _read_counter_file(self) -> Dict[str, Any]:
        """Read counter data from file"""
        try:
            with open(self.counter_file, 'r') as f:
                data = json.load(f)
                # Ensure counter key exists
                if 'counter' not in data:
                    data['counter'] = 0
                return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Error reading counter file: {e}")
            return {"counter": 0}
    
    def write_counter_file(self, data: Dict[str, Any]):
        """Write counter data to file"""
        try:
            with open(self.counter_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing counter file: {e}")
            raise
    
    def get_counter(self) -> int:
        """Get current counter value"""
        with self.lock:
            data = self._read_counter_file()
            counter = data.get('number', 0)
            logger.debug(f"Current counter: {counter}")
            return counter
    
    def set_counter(self, value: int) -> int:
        """Set counter to specific value"""
        with self.lock:
            data = self._read_counter_file()
            data['counter'] = value
            data['last_updated'] = self._get_timestamp()
            self._write_counter_file(data)
            logger.info(f"Counter set to: {value}")
            return value
    
    def increment_counter(self) -> int:
        """Increment counter by 1 and return new value"""
        with self.lock:
            data = self._read_counter_file()
            data['counter'] = data.get('counter', 0) + 1
            data['last_updated'] = self._get_timestamp()
            self._write_counter_file(data)
            new_value = data['counter']
            logger.info(f"Counter incremented to: {new_value}")
            return new_value
    
    def get_counter_data(self) -> Dict[str, Any]:
        """Get full counter data including metadata"""
        with self.lock:
            return self._read_counter_file()
    
    def _get_timestamp(self) -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.now().isoformat()
