# OpenAI API to MQTT Bridge

[![mypy](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/mypy.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/mypy.yml) [![flake8](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/flake8.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/flake8.yml) [![black](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/black.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/black.yml) [![codeql](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/codeql.yml/badge.svg)](https://github.com/jinglemansweep/openai2mqtt/actions/workflows/codeql.yml) [![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Provides an MQTT interface for interacting with OpenAI services (including ChatGPT and Assistants).

## Development

Create a Python 3.x virtual environment, and install project dependencies:

    python3 -m venv venv
    . venv/bin/activate
    pip install --upgrade pip poetry
    poetry install

## Running

To run the project:

    . venv/bin/activate
    python3 -m openai2mqtt

TEST
