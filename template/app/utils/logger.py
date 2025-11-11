import logging


def configure_logging() -> logging.Logger:
    logger = logging.getLogger("{{APP-NAME}}")
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s ",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("{{APP-NAME}}.log"),
        ],
    )

    logger_blocklist = ["asyncio", "urllib3"]
    for module in logger_blocklist:
        logging.getLogger(module).setLevel(logging.WARNING)
    return logger


logger = configure_logging()
