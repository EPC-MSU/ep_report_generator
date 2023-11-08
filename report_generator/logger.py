import logging


def set_logger() -> None:
    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)
    package_logger = logging.getLogger("report_generator")
    package_logger.setLevel(logging.INFO)
    package_logger.addHandler(handler)
    package_logger.propagate = False
