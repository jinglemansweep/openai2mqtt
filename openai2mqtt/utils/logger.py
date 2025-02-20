import logging

LOG_FORMAT = "%(name)-20s %(levelname)-7s %(message)s"


def setup_logger(debug: bool = False) -> None:
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(level=log_level, format=LOG_FORMAT)
    logging.getLogger("openai").setLevel(logging.ERROR)
    logging.getLogger("httpx").setLevel(logging.ERROR)
    logging.getLogger("httpcore").setLevel(logging.ERROR)
