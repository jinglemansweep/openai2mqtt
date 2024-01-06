# OpenAI API to MQTT Bridge

[![mypy](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/mypy.yml) [![flake8](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/flake8.yml) [![black](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/black.yml) [![codeql](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/codeql.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/codeql.yml) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Provides an MQTT interface for interacting with OpenAI services (including ChatGPT and Assistants).

## Usage

### MQTT

#### Topic: `<prefix>/assistant/message/<session-id>`

Publishes a message to the provided session. If the session does not exist, one is created and associated with the `session-id` (NOTE: persisted to Redis)

If session does not exist, an OpenAI Assistant [Thread](https://platform.openai.com/docs/api-reference/threads) is created and maintained.

The posted message is then created as a [Message](https://platform.openai.com/docs/api-reference/messages) and appended to the new or existing thread.

A [Run](https://platform.openai.com/docs/api-reference/runs) is then created and launched to send the thread contents to OpenAI APIs. This Run is associated with the Session and is periodically polled.

If the Run status equals `complete`, retrieve any response Messages and publish them to the MQTT topic: `<prefix>/assistant/response/<session-id>`

TODO: Handle `requires-action`

Payload:

    {
        "message": "string",
        "assistant_id": "string"
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
