import logging
from .constants import (
    AppMetadata,
)
from .config import settings
from .utils.logger import setup_logger

# Logging
setup_logger(debug=settings.general.debug)
logger = logging.getLogger(AppMetadata.NAME)

logger.info("HELLO")
