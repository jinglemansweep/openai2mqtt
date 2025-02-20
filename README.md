# OpenAI API to MQTT Bridge

[![mypy](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/mypy.yml) [![flake8](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/flake8.yml) [![black](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/black.yml) [![codeql](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/codeql.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/codeql.yml) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Provides an MQTT interface for interacting with OpenAI services (including ChatGPT and Assistants).

## Usage

### MQTT

#### Publish

##### `openai2mqtt/assistant/create`

Create a new assistant.

    {
        "name": "My Assistant",
        "instructions": "You are a personal math tutor. Write and run code to answer math questions.",
        "model": "gpt-4o-mini"
    }

##### `openai2mqtt/thread/create`

Create a new thread.

##### `openai2mqtt/thread/message`

Post a new message to an assistant thread.

    {
        "assistant_id": "asst_zDOIzdnXWGXXOo1bOGwRdbRH",
        "thread_id": "thread_QS1ZI0oSxMxo0npePrtPVpMp",
        "role": "user",
        "content": "How big is a box?"
    }

#### Subscribe

##### `openai2mqtt/assistant/status`

Status of assistant management actions.

    {
        "id": "asst_zDOIzdnXWGXXOo1bOGwRdbRH",
        "name": "My Assistant",
        "model": "gpt-4o-mini"
    }

##### `openai2mqtt/thread/status`

Status of thread management actions.

    {
        "id": "thread_QS1ZI0oSxMxo0npePrtPVpMp",
        "metadata": {}
    }

##### `openai2mqtt/thread/run/<thread-id>`

Status of thread run for thread `<thread-id>`.

    {
        "id": "run_1234567890",
        "status": "completed"
    }

##### `openai2mqtt/thread/message/<thread-id>`

Message reply from model for `<thread-id>`.

    {
        "id": "msg_1234567890",
        "content": "Example response"
    }

## Development

Create a Python 3.x virtual environment, install project dependencies and `pre-commit` hooks:

    python3 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip poetry
    poetry install
    pre-commit install -t commit-msg -t pre-commit

## Running

To run the project:

    . venv/bin/activate
    python3 -m openai2mqtt
