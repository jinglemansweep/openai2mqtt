import logging
from paho.mqtt.client import Client
from pydantic import BaseModel
from typing import Dict
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
logger.info(f"settings.general: debug={settings.general.debug}")
logger.info(
    f"settings.mqtt: host={settings.mqtt.host}:{settings.mqtt.port} user={settings.mqtt.username} topic_prefix={settings.mqtt.topic_prefix} keepalive={settings.mqtt.keepalive}"
)

# Models


class Message(BaseModel):
    content: str
    assistant_id: str


# Store

store: Dict = dict(sessions=dict())

# MQTT


def on_ping(client):
    logger.info("action: type=pong")
    client.publish(f"{settings.mqtt.topic_prefix}/pong")


def on_message(client, payload):
    try:
        message = Message.model_validate_json(payload)
    except Exception as e:
        logger.error(f"error: type=invalid_message payload={payload}", exc_info=e)
        return
    logger.info(f"action: type=message message={message.model_dump()}")


def on_mqtt_message(client, userdata, message):
    topic = message.topic[len(settings.mqtt.topic_prefix) + 1 :]
    payload = message.payload.decode()
    logger.debug(
        f"mqtt.message: prefix={settings.mqtt.topic_prefix} topic={topic} payload={payload}"
    )
    if topic.startswith("ping"):
        on_ping(client)
    elif topic.startswith("message"):
        on_message(client, payload)


mqtt_client = Client(client_id=settings.mqtt.client_id)
mqtt_client.on_message = on_mqtt_message
if settings.mqtt.username is not None:
    mqtt_client.username_pw_set(settings.mqtt.username, settings.mqtt.password)
mqtt_client.connect(settings.mqtt.host, settings.mqtt.port, settings.mqtt.keepalive)

mqtt_client.subscribe(f"{settings.mqtt.topic_prefix}/#")

while True:
    mqtt_client.loop()
