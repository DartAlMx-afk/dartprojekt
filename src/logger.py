import logging
import os
import sys

def setup_logger():
    # Ensure logs directory exists
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, "app.log")

    logger = logging.getLogger("AI_Text_Corrector")
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_file_path, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

logger = setup_logger()
logger.debug("Logger initialized successfully. Logging to logs/app.log")
