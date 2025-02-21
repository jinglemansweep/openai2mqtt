import aiomqtt
import asyncio
import json
import logging
from openai import OpenAI
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
    get_thread,
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


class ThreadMessage(BaseModel):
    assistant_id: str
    role: str = "user"
    content: str


# Store

store: Dict = dict(assistants=dict(), threads=dict())
store["assistants"] = get_assistants(openai_client)

# MQTT


async def api_ping(mqtt_client):
    logger.info("api.ping: result=pong")
    mqtt_client.publish(f"{settings.mqtt.topic_prefix}/pong")


async def api_assistant_create(mqtt_client, topic, payload):
    try:
        config = Assistant.model_validate_json(payload)
    except Exception as e:
        logger.error(f"error: type=invalid_message payload={payload}", exc_info=e)
        return
    logger.debug(f"api.assistant.create: config={config.model_dump()}")
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
            f"{settings.mqtt.topic_prefix}/api/assistant/status",
            payload=json.dumps(
                dict(id=assistant.id, name=assistant.name, model=assistant.model)
            ),
        )
        logger.info(f"Assistant '{config.name}' created")


async def api_thread_create(mqtt_client, topic, payload):
    logger.debug("api.thread.create")
    thread = openai_client.beta.threads.create()
    await mqtt_client.publish(
        f"{settings.mqtt.topic_prefix}/api/thread/status",
        payload=json.dumps(dict(id=thread.id, metadata=thread.metadata)),
    )
    logger.info(f"Thread '{thread.id}' created")
    return thread


async def thread_handler(mqtt_client, topic, payload):
    _, thread_id, action = topic.split("/")

    if action == "post":
        try:
            message = ThreadMessage.model_validate_json(payload)
        except Exception as e:
            logger.error(
                f"error: type=invalid_thread_action payload={payload}", exc_info=e
            )
            return
        logger.debug(
            f"thread.handler: assistant_id={message.assistant_id} thread_id={thread_id} action={action}"
        )
        assistant = get_assistant(openai_client, message.assistant_id)
        thread = get_thread(openai_client, thread_id)
        await thread_post(mqtt_client, assistant, thread, message)


async def thread_post(mqtt_client, assistant, thread, message):
    openai_client.beta.threads.messages.create(
        thread_id=thread.id, role=message.role, content=message.content
    )
    run = openai_client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )
    while run.status != "completed":
        run = openai_client.beta.threads.runs.retrieve(
            thread_id=thread.id, run_id=run.id
        )
        logger.debug(f"thread.run.status: id={run.id} status={run.status}")
        await mqtt_client.publish(
            f"{settings.mqtt.topic_prefix}/thread/{thread.id}/run",
            json.dumps(dict(id=run.id, status=run.status)),
        )
        await asyncio.sleep(1)

    messages = list(
        openai_client.beta.threads.messages.list(
            thread_id=thread.id, order="desc", limit=5
        )
    )
    filtered_messages = messages[:1]

    for m in filtered_messages:
        logger.info(f"thread.message: id={m.id} content={m.content[0].text.value}")
        await mqtt_client.publish(
            f"{settings.mqtt.topic_prefix}/thread/{thread.id}/message",
            json.dumps(dict(id=m.id, content=m.content[0].text.value)),
        )


async def handle_message(message, mqtt_client):
    topic = str(message.topic)[len(settings.mqtt.topic_prefix) + 1 :]
    payload = message.payload.decode()
    logger.debug(
        f"mqtt.message: prefix={settings.mqtt.topic_prefix} topic={topic} payload={payload}"
    )
    if topic.startswith("ping"):
        await api_ping(mqtt_client)
    elif topic.startswith("api/assistant/create"):
        await api_assistant_create(mqtt_client, topic, payload)
    elif topic.startswith("api/thread/create"):
        await api_thread_create(mqtt_client, topic, payload)
    elif topic.startswith("thread"):
        await thread_handler(mqtt_client, topic, payload)


async def main():

    async with aiomqtt.Client(
        hostname=settings.mqtt.host,
        port=settings.mqtt.port,
        username=settings.mqtt.username,
        password=settings.mqtt.password,
    ) as mqtt_client:
        await mqtt_client.subscribe(f"{settings.mqtt.topic_prefix}/#")
        async for message in mqtt_client.messages:
            await handle_message(message, mqtt_client)


asyncio.run(main())
