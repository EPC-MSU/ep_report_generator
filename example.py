"""
File with example how to work with report generator.
"""

import os
import sys
from datetime import timedelta
from PyQt5.QtWidgets import QApplication
from epcore.filemanager import load_board_from_ufiv
from report_generator import ConfigAttributes, create_test_and_ref_boards, ObjectsForReport, ReportGenerator
from manual_board import create_manual_board


if __name__ == "__main__":

    app = QApplication(sys.argv)
    report_generator = ReportGenerator()
    # Report for board from P10 file
    BOARD_FILE_NAME = "example_board/elements.json"
    # report_generator.open_board_file(BOARD_FILE_NAME)
    dir_name = os.path.dirname(os.path.abspath(__file__))
    dir_for_report = os.path.join(dir_name, "report_for_p10_board")
    board = load_board_from_ufiv(BOARD_FILE_NAME)
    test_board, ref_board = create_test_and_ref_boards(board)
    config = {ConfigAttributes.BOARD_TEST: test_board,
              ConfigAttributes.BOARD_REF: ref_board,
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                         ObjectsForReport.ELEMENT: [],
                                         ObjectsForReport.PIN: []},
              ConfigAttributes.THRESHOLD_SCORE: 0.5,
              ConfigAttributes.PIN_SIZE: 200,
              ConfigAttributes.OPEN_REPORT_AT_FINISH: True,
              ConfigAttributes.APP_NAME: "EyePoint H10",
              ConfigAttributes.APP_VERSION: "1.2.3",
              ConfigAttributes.TEST_DURATION: timedelta(seconds=562)}
    report_generator.run(config)

    # Report for manual board
    report_generator = ReportGenerator()
    dir_for_report = os.path.join(dir_name, "report_for_manual_board")
    test_board = create_manual_board(True)
    ref_board = create_manual_board(False)
    config = {ConfigAttributes.BOARD_TEST: test_board,
              ConfigAttributes.BOARD_REF: ref_board,
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                         ObjectsForReport.ELEMENT: [],
                                         ObjectsForReport.PIN: []},
              ConfigAttributes.THRESHOLD_SCORE: 0.2}
    report_generator.run(config)
