import logging
import sys

# Create logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Create stdout handler
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))

# Avoid duplicate handlers
if not logger.handlers:
    logger.addHandler(handler)

# Now use logger
logger.info("App started successfully!")
