"""
File with example how to work with report generator.
"""

import os
import sys
from datetime import timedelta
from PyQt5.QtWidgets import QApplication
from epcore.filemanager import load_board_from_ufiv
from report_generator import (ConfigAttributes, create_test_and_ref_boards, ObjectsForReport, ReportGenerator,
                              ReportTypes, ScalingTypes)
from manual_board import create_manual_board


if __name__ == "__main__":

    app = QApplication(sys.argv)
    # Report for board from P10 file
    BOARD_FILE_NAME = "example_board/elements.json"
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
              ConfigAttributes.APP_NAME: "EyePoint P10",
              ConfigAttributes.APP_VERSION: "1.2.3",
              ConfigAttributes.TEST_DURATION: timedelta(seconds=562),
              ConfigAttributes.SCALING_TYPE: ScalingTypes.EYEPOINT_P10,
              ConfigAttributes.ENGLISH: True}
    report_generator = ReportGenerator()
    report_generator.run(config)

    # Report for manual board
    dir_for_report = os.path.join(dir_name, "report_for_manual_board")
    test_board = create_manual_board(True)
    ref_board = create_manual_board(False)
    config = {ConfigAttributes.BOARD_TEST: test_board,
              ConfigAttributes.BOARD_REF: ref_board,
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                         ObjectsForReport.ELEMENT: [],
                                         ObjectsForReport.PIN: []},
              ConfigAttributes.THRESHOLD_SCORE: 0.2,
              ConfigAttributes.OPEN_REPORT_AT_FINISH: True,
              ConfigAttributes.REPORTS_TO_OPEN: [ReportTypes.FULL_REPORT, ReportTypes.SHORT_REPORT]}
    report_generator.run(config)

    # Report for manual board with user defined scales
    dir_for_report = os.path.join(dir_name, "report_for_manual_board_with_user_defined_scales")
    test_board = create_manual_board(True)
    ref_board = create_manual_board(False)
    # Define scales for each pin
    user_defined_scales = []
    for element in test_board.elements:
        for pin in element.pins:
            if not pin.measurements:
                user_defined_scales.append(None)
                continue
            max_voltage = pin.measurements[0].settings.max_voltage
            internal_resistance = pin.measurements[0].settings.internal_resistance
            user_defined_scales.append((1.6 * max_voltage, 1.6 * max_voltage / internal_resistance))
    config = {ConfigAttributes.BOARD_TEST: test_board,
              ConfigAttributes.BOARD_REF: ref_board,
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                         ObjectsForReport.ELEMENT: [],
                                         ObjectsForReport.PIN: []},
              ConfigAttributes.SCALING_TYPE: ScalingTypes.USER_DEFINED,
              ConfigAttributes.THRESHOLD_SCORE: 0.2,
              ConfigAttributes.USER_DEFINED_SCALES: user_defined_scales}
    report_generator.run(config)
