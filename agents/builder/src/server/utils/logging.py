import logging
import sys


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="\033[36m%(asctime)s.%(msecs)03d\033[0m [\033[33m%(levelname)s\033[0m] %(message)s",
        datefmt="%H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger(__name__)
