import logging

from pytasched.server import PytaschedServer
from pytasched import settings


def _get_logger():
    """
    Get a logger that produces reasonable output.

    :return logging.Logger:
    """
    logger = logging.getLogger(__name__)

    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(
        logging.Formatter('%(asctime)s [%(levelname)8s] %(message)s')
    )

    logger.addHandler(ch)
    logger.setLevel(logging.DEBUG)

    return logger


if __name__ == "__main__":
    logger = _get_logger()
    server = PytaschedServer(settings, logger)

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Exiting...")
