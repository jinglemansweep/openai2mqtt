import json
import logging
import time
from openai import OpenAI
from paho.mqtt.client import Client
from pydantic import BaseModel
from typing import Dict
from .constants import (
    AppMetadata,
)
from .config import settings
from .utils.logger import setup_logger
from .utils.openai_api import (
    get_assistants,
    get_assistant,
    get_threads,
    get_thread,
    get_assistant_by_name,
)

# Notes

# /assistant/create -> create Assistant
# /assistant/post -> post Message to Assistant
# /assistant/thread/reset

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


# Models


class Assistant(BaseModel):
    name: str = "default"
    description: str = "Default Assistant"
    instructions: str = "You are a helpful assistant."
    model: str = "gpt-4o-mini"


class Message(BaseModel):
    assistant_id: str
    thread_id: str
    content: str


# Store

store: Dict = dict(assistants=dict(), threads=dict())
store["assistants"] = get_assistants(openai_client)

# MQTT


def ping(mqtt_client):
    logger.info("action: type=pong")
    mqtt_client.publish(f"{settings.mqtt.topic_prefix}/pong")


def assistant_create(mqtt_client, topic, payload):
    try:
        config = Assistant.model_validate_json(payload)
    except Exception as e:
        logger.error(f"error: type=invalid_message payload={payload}", exc_info=e)
        return
    logger.debug(f"assistant.create: config={config.model_dump()}")
    name_lower = config.name.lower()
    if len([a for a in store["assistants"] if a.name == name_lower]) > 0:
        logger.info(f"Assistant '{name_lower}' already exists")
        return
    else:
        assistant = openai_client.beta.assistants.create(
            name=name_lower,
            description=config.description,
            instructions=config.instructions,
            # tools=[{"type": "code_interpreter"}],
            model=config.model,
        )
        store["assistants"] = get_assistants(openai_client)
        mqtt_client.publish(
            f"{settings.mqtt.topic_prefix}/assistant/status",
            payload=json.dumps(
                dict(id=assistant.id, name=assistant.name, model=assistant.model)
            ),
        )
        logger.info(f"Assistant '{config.name}' created")


def thread_create(mqtt_client, topic, payload):
    logger.debug(f"thread.create")
    thread = openai_client.beta.threads.create()
    mqtt_client.publish(
        f"{settings.mqtt.topic_prefix}/thread/status",
        payload=json.dumps(dict(id=thread.id, metadata=thread.metadata)),
    )
    logger.info(f"Thread '{thread.id}' created")
    return thread


def thread_message(mqtt_client, topic, payload):
    try:
        message = Message.model_validate_json(payload)
    except Exception as e:
        logger.error(f"error: type=invalid_message payload={payload}", exc_info=e)
        return
    logger.debug(
        f"thread.message: assistant_id={message.assistant_id} thread_id={message.thread_id} content={message.content}"
    )
    assistant = get_assistant(openai_client, message.assistant_id)
    thread = get_thread(openai_client, message.thread_id)
    openai_client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=message.content
    )
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while run.status != "completed":
        logger.debug(f"thread.run.status: id={run.id} status={run.status}")
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )
        time.sleep(1)
    messages = list(
        openai_client.beta.threads.messages.list(thread_id=thread.id, order="desc")
    )
    filtered_messages = messages[:1]

    for m in filtered_messages:
        logger.info(f"thread.message: id={m.id} content={m.content[0].text.value}")
        mqtt_client.publish(
            f"{settings.mqtt.topic_prefix}/thread/reply",
            m.content[0].text.value,
        )


def on_mqtt_message(mqtt_client, userdata, message):
    topic = message.topic[len(settings.mqtt.topic_prefix) + 1 :]
    payload = message.payload.decode()
    logger.debug(
        f"mqtt.message: prefix={settings.mqtt.topic_prefix} topic={topic} payload={payload}"
    )
    if topic.startswith("ping"):
        ping(mqtt_client)
    elif topic.startswith("assistant/create"):
        assistant_create(mqtt_client, topic, payload)
    elif topic.startswith("thread/create"):
        thread_create(mqtt_client, topic, payload)
    elif topic.startswith("thread/message"):
        thread_message(mqtt_client, topic, payload)


mqtt_client = Client(client_id=settings.mqtt.client_id)
mqtt_client.on_message = on_mqtt_message
if settings.mqtt.username is not None:
    mqtt_client.username_pw_set(settings.mqtt.username, settings.mqtt.password)
mqtt_client.connect(settings.mqtt.host, settings.mqtt.port, settings.mqtt.keepalive)

mqtt_client.subscribe(f"{settings.mqtt.topic_prefix}/#")

logger.debug(f"config: {settings.as_dict()}")

mqtt_client.loop_forever()
