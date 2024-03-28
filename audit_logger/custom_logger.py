import logging


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, "INFO", logging.ERROR))

    # No duplicated handlers plz.
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(levelname)s:     %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
