import os
import sys
import logging
from .config import config


logging_str = "[%(asctime)s: %(levelname)s: %(module)s: %(message)s]"
log_dir = config.log_dir
log_file_path = os.path.join(log_dir, 'ai_powered_data_assistant.log')
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format=logging_str,
    handlers=[
        logging.FileHandler(log_file_path),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('ai_powered_data_assistant_logger')