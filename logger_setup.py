import logging
import sys

def setup_logger():
 
    logger = logging.getLogger()
    if logger.hasHandlers():
        # If handlers are already set, do not add them again
        return logger

    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # File handler (kept as the only handler)
    file_handler = logging.FileHandler('logs/bot.log', mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Setup the logger when the module is imported
logger = setup_logger()