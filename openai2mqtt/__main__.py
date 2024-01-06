import logging
from .constants import (
    AppMetadata,
)
from .config import settings
from .utils.logger import setup_logger

# Logging
setup_logger(debug=settings.general.debug)
logger = logging.getLogger(AppMetadata.NAME)

# Startup
logger.info(f"{AppMetadata.TITLE} v{AppMetadata.VERSION}")
logger.info(f"Debug: {settings.general.debug}")
logger.info(
    f"MQTT: Host={settings.mqtt.host}:{settings.mqtt.port} User={settings.mqtt.username}, Topic={settings.mqtt.topic_prefix}/#)"
)
