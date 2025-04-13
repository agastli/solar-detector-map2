# src/utils/logger.py
import logging

# Create logger
logger = logging.getLogger("solar_detector")
logger.setLevel(logging.DEBUG)

# Create handler (console)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)

# Attach handler to logger
logger.addHandler(console_handler)
