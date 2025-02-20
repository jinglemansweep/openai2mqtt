import logging
from openai import OpenAI
from paho.mqtt.client import Client
from pydantic import BaseModel
from typing import Dict
from .constants import (
    AppMetadata,
)
from .config import settings
from .utils.logger import setup_logger
from .utils.openai_api import get_assistants, get_assistant_by_name

# Logging
setup_logger(debug=settings.general.debug)
logger = logging.getLogger(AppMetadata.NAME)

# Startup
logger.info(f"{AppMetadata.TITLE} v{AppMetadata.VERSION}")
logger.info(f"settings.general: debug={settings.general.debug}")
logger.info(
    f"settings.mqtt: host={settings.mqtt.host}:{settings.mqtt.port} user={settings.mqtt.username} topic_prefix={settings.mqtt.topic_prefix} keepalive={settings.mqtt.keepalive}"
)

# OpenAI
openai_client = OpenAI(api_key=settings.openai_api_key)

# thread = client.beta.threads.create()

# Models


class Assistant(BaseModel):
    name: str = "default"
    description: str = "Default Assistant"
    instructions: str = "You are a helpful assistant."
    model: str = "gpt-4o-mini"


class Message(BaseModel):
    content: str


# Store

store: Dict = dict(assistants=dict(), threads=dict())

store["assistants"] = get_assistants(openai_client)

for a in store["assistants"]:
    print(a.name)

search = "Test Assistant"
found = any([a.name == search for a in store["assistants"]])
print(found)

ass2 = get_assistant_by_name(openai_client, "test2")

# MQTT


def on_ping(client):
    logger.info("action: type=pong")
    client.publish(f"{settings.mqtt.topic_prefix}/pong")


def thread_message(client, topic, payload):
    try:
        message = Message.model_validate_json(payload)
    except Exception as e:
        logger.error(f"error: type=invalid_message payload={payload}", exc_info=e)
        return
    assistant_id = topic.split("/")[1]
    assistant = get_assistant_by_name(openai_client, assistant_id)
    logger.debug(
        f"action: type=message assistant={assistant_id} message={message.model_dump()}"
    )
    thread = openai_client.beta.threads.create()
    openai_client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=message.content
    )
    print(assistant, thread)
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    if run.status == "completed":
        print("COMP")
    messages = openai_client.beta.threads.messages.list(thread_id=thread.id)
    for m in messages:
        client.publish(
            f"{settings.mqtt.topic_prefix}/{assistant_id}/thread",
            m.content[0].text.value,
        )


def create_assistant(client, payload):
    try:
        config = Assistant.model_validate_json(payload)
    except Exception as e:
        logger.error(f"error: type=invalid_message payload={payload}", exc_info=e)
        return
    logger.debug(f"create_assistant: config={config.model_dump()}")

    if len([a for a in store["assistants"] if a.name == config.name]) > 0:
        logger.info(f"Assistant '{config.name}' already exists")
        return
    else:

        assistant = openai_client.beta.assistants.create(
            name=config.name,
            instructions=config.instructions,
            # tools=[{"type": "code_interpreter"}],
            model=config.model,
        )
        store["assistants"].append(assistant)
        logger.info(f"Assistant '{config.name}' created")


def on_mqtt_message(client, userdata, message):
    topic = message.topic[len(settings.mqtt.topic_prefix) + 1 :]
    payload = message.payload.decode()
    logger.debug(
        f"mqtt.message: prefix={settings.mqtt.topic_prefix} topic={topic} payload={payload}"
    )
    if topic.startswith("ping"):
        on_ping(client)
    elif topic.startswith("assistant"):
        create_assistant(client, payload)
    elif topic.startswith("message"):
        thread_message(client, topic, payload)


mqtt_client = Client(client_id=settings.mqtt.client_id)
mqtt_client.on_message = on_mqtt_message
if settings.mqtt.username is not None:
    mqtt_client.username_pw_set(settings.mqtt.username, settings.mqtt.password)
mqtt_client.connect(settings.mqtt.host, settings.mqtt.port, settings.mqtt.keepalive)

mqtt_client.subscribe(f"{settings.mqtt.topic_prefix}/#")

logger.debug(f"config: {settings.as_dict()}")

mqtt_client.loop_forever()
