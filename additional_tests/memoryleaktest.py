"""
File with example how to work with report generator.
"""

import argparse
import logging
import os
import sys
import time
from datetime import timedelta
import psutil
from PyQt5.QtWidgets import QApplication
repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(repo_dir)
if True:
    from epcore.filemanager import load_board_from_ufiv
    from report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator, ScalingTypes, set_logging_level


def get_memory() -> int:
    """
    :return: the non-swapped physical memory a process has used.
    """

    process = psutil.Process(os.getpid())
    return process.memory_info().rss


def set_logger_for_analyzer(log_file: str) -> None:
    """
    :param log_file: file name where to save memory leak testing logs.
    """

    formatter = logging.Formatter("[%(asctime)s %(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    logger = logging.getLogger("analyzer")
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(handler)
    logger.propagate = False


def run_test(reports_number: int) -> None:
    """
    :param reports_number: number of reports to be generated.
    """

    # Report for board from P10 file
    dir_for_report = os.path.join(os.getcwd(), "examples", "report_for_p10_board")
    config = {ConfigAttributes.BOARD: load_board_from_ufiv(os.path.join("example_board", "elements.json")),
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True},
              ConfigAttributes.PIN_SIZE: 200,
              ConfigAttributes.OPEN_REPORT_AT_FINISH: False,
              ConfigAttributes.APP_NAME: "EyePoint P10",
              ConfigAttributes.APP_VERSION: "1.2.3",
              ConfigAttributes.TEST_DURATION: timedelta(seconds=562),
              ConfigAttributes.SCALING_TYPE: ScalingTypes.EYEPOINT_P10,
              ConfigAttributes.ENGLISH: True}
    report_generator = ReportGenerator()

    logger = logging.getLogger("analyzer")
    logger.info("Start")
    for i in range(1, reports_number + 1):
        report_generator.run(config)
        memory = get_memory() / pow(2, 20)
        logger.info("Report #%d, memory = %f MB", i, memory)
        time.sleep(1)
    logger.info("Finish")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("reports_number", type=int, help="Number of reports to be generated")
    parsed_args = parser.parse_args(sys.argv[1:])

    set_logging_level(logging.ERROR)
    set_logger_for_analyzer("memory_leak_log.txt")
    app = QApplication(sys.argv)
    run_test(parsed_args.reports_number)
