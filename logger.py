import logging
from pathlib import Path

LOG_PATH = Path(__file__).parent / "confessor-notebook.log"


def get_logger():
    logger = logging.getLogger("confessor-notebook")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fh = logging.FileHandler(LOG_PATH, encoding="utf-8")
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
