import logging
from typing import Optional


def save_logs_to_file(log_file: Optional[str] = None) -> None:
    """
    :param log_file: path to the file where the logs will be saved.
    """

    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)
    package_logger = logging.getLogger("report_generator")
    package_logger.addHandler(file_handler)


def set_logger() -> None:
    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    package_logger = logging.getLogger("report_generator")
    package_logger.setLevel(logging.INFO)
    package_logger.addHandler(handler)
    package_logger.propagate = False
