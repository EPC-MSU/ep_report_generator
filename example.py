"""
File with example how to work with report generator.
"""

import os
import sys
from datetime import timedelta
from PyQt5.QtWidgets import QApplication
from epcore.elements import Board
from epcore.filemanager import load_board_from_ufiv
from report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator, ReportTypes, ScalingTypes
from manual_board import create_manual_board
from report_generator.logger import save_logs_to_file


if __name__ == "__main__":

    save_logs_to_file("log.txt")
    app = QApplication(sys.argv)
    dir_name = os.path.dirname(os.path.abspath(__file__))

    # Report for board from P10 file
    dir_for_report = os.path.join(dir_name, "examples", "report_for_p10_board")
    config = {ConfigAttributes.BOARD: load_board_from_ufiv(os.path.join("example_board", "elements.json")),
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True},
              ConfigAttributes.PIN_SIZE: 200,
              ConfigAttributes.OPEN_REPORT_AT_FINISH: True,
              ConfigAttributes.APP_NAME: "EyePoint P10",
              ConfigAttributes.APP_VERSION: "1.2.3",
              ConfigAttributes.TEST_DURATION: timedelta(seconds=562),
              ConfigAttributes.SCALING_TYPE: ScalingTypes.EYEPOINT_P10,
              ConfigAttributes.ENGLISH: True}
    report_generator = ReportGenerator()
    report_generator.run(config)
    sys.exit(0)

    # Report for manual board
    dir_for_report = os.path.join(dir_name, "examples", "report_for_manual_board")
    config = {ConfigAttributes.BOARD: create_manual_board(),
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.ELEMENT: [0, 2],
                                         ObjectsForReport.PIN: []},
              ConfigAttributes.THRESHOLD_SCORE: 0.15,
              ConfigAttributes.OPEN_REPORT_AT_FINISH: True,
              ConfigAttributes.REPORTS_TO_OPEN: [ReportTypes.FULL_REPORT, ReportTypes.SHORT_REPORT]}
    report_generator.run(config)

    # Report for manual board with user defined scales
    dir_for_report = os.path.join(dir_name, "examples", "report_for_manual_board_with_user_defined_scales")
    board = create_manual_board()
    # Define scales for each pin
    required_pins = [3, 4, 5]
    user_defined_scales = []
    total_pin_index = 0
    for element in board.elements:
        for pin in element.pins:
            if total_pin_index in required_pins:
                if not pin.measurements:
                    user_defined_scales.append(None)
                    continue
                max_voltage = pin.measurements[0].settings.max_voltage
                internal_resistance = pin.measurements[0].settings.internal_resistance
                user_defined_scales.append((1.6 * max_voltage, 1.6 * max_voltage / internal_resistance))
    config = {ConfigAttributes.BOARD: board,
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.ELEMENT: [],
                                         ObjectsForReport.PIN: required_pins},
              ConfigAttributes.SCALING_TYPE: ScalingTypes.USER_DEFINED,
              ConfigAttributes.THRESHOLD_SCORE: 0.15,
              ConfigAttributes.USER_DEFINED_SCALES: user_defined_scales}
    report_generator.run(config)

    # Report for empty board
    dir_for_report = os.path.join(dir_name, "examples", "report_for_empty_board")
    config = {ConfigAttributes.BOARD: Board(),
              ConfigAttributes.DIRECTORY: dir_for_report,
              ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True}}
    report_generator.run(config)
