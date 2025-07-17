import logging
import sys

def setup_logger():
    """
    Configures the logger to output to both console and a file.
    """
    logger = logging.getLogger()
    if logger.hasHandlers():
        # If handlers are already set, do not add them again
        return logger

    logger.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler
    file_handler = logging.FileHandler('logs/bot.log', mode='a')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Setup the logger when the module is imported
logger = setup_logger()