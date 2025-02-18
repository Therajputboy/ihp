import logging
import json
import sys

# Configure logging for Cloud Run
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s',
    stream=sys.stdout  # Ensure logs go to stdout for Cloud Run
)

logger = logging.getLogger(__name__)