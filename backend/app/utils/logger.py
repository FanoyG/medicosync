import os
import logging
from datetime import datetime

def setup_logging():
    # 1. Define the production root logs directory
    log_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))
    
    # Ensure the logs directory exists automatically
    os.makedirs(log_dir, exist_ok=True)

    # 2. Generate filename standard format: Day_Date_Month_Year.log (e.g., Saturday_16_05_2026.log)
    # %A = Full weekday name in English
    # %d = Day of the month
    # %m = Month as a number
    # %Y = Four-digit year
    current_time = datetime.now()
    log_filename = current_time.strftime("%A_%d_%m_%Y.log")
    full_log_path = os.path.join(log_dir, log_filename)

    # 3. Create a clean, comprehensive production format
    log_format = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"

    # 4. Configure the root logger engine
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(full_log_path, encoding='utf-8')
        ]
    )

# Execute the setup to initialize the file handler system
setup_logging()
logger = logging.getLogger("medicosync")
    