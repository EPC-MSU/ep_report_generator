"""
File with example how to work with report generator.
"""

import os
import sys
from PyQt5.QtWidgets import QApplication
from epcore.filemanager import load_board_from_ufiv
from report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator


if __name__ == "__main__":

    app = QApplication(sys.argv)
    report_generator = ReportGenerator()
    BOARD_FILE_NAME = "example_board/elements.json"
    # report_generator.open_board_file(BOARD_FILE_NAME)
    dir_for_report = os.path.join(os.path.dirname(os.path.abspath(__file__)), "report")
    board = load_board_from_ufiv(BOARD_FILE_NAME)
    config = {ConfigAttributes.BOARD_TEST: board,
              ConfigAttributes.BOARD_REF: board,
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                         ObjectsForReport.ELEMENT: [],
                                         ObjectsForReport.PIN: []},
              ConfigAttributes.THRESHOLD_SCORE: 0.5,
              }
    report_generator.run(config)
