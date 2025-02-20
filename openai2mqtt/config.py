from dynaconf import Dynaconf, Validator
from .constants import DYNACONF_ENVVAR_PREFIX


validators = [
    # General
    Validator(
        "GENERAL__DEBUG",
        default=False,
        cast=bool,
    ),
    # MQTT
    Validator(
        "MQTT__HOST",
        default="localhost",
        cast=str,
    ),
    Validator(
        "MQTT__PORT",
        default=1883,
        cast=int,
    ),
    Validator(
        "MQTT__USERNAME",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT__PASSWORD",
        default=None,
        cast=str,
    ),
    Validator(
        "MQTT__CLIENT_ID",
        default="openai2mqtt",
        cast=str,
    ),
    Validator(
        "MQTT__TOPIC_PREFIX",
        default="openai2mqtt",
        cast=str,
    ),
    Validator(
        "MQTT__KEEPALIVE",
        default=60,
        cast=int,
    ),
    # API
    Validator("OPENAI_API_KEY", default=None, cast=str),
]


settings = Dynaconf(
    envvar_prefix=DYNACONF_ENVVAR_PREFIX,
    settings_files=["settings.toml", "settings.local.toml", "secrets.toml"],
    validators=validators,
)
