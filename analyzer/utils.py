from datetime import datetime
from typing import List


def convert_to_datetime(datetime_str: str) -> datetime:
    return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")


def read_log_file(file_name: str) -> List[str]:
    """
    :param file_name: file name with logs.
    :return: list of messages from file.
    """

    with open(file_name, "r", encoding="utf-8") as file:
        content = file.read()
    return content.split("\n")
