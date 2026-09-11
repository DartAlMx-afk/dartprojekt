import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

from src.gui import run_app
from src.logger import logger

def main():
    logger.info("Starting AI Text Corrector application.")
    try:
        run_app()
    except Exception as e:
        logger.critical(f"Application crashed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
