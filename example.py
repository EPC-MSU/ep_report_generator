"""
File with example how to work with report generator.
"""

import sys
from PyQt5.QtWidgets import QApplication
from report_generator import ConfigAttributes, ReportGenerator, RequirementTypes


if __name__ == "__main__":

    app = QApplication(sys.argv)
    report_generator = ReportGenerator()
    report_generator.threshold_score = 0.4
    BOARD_FILE_NAME = "example_board/elements.json"
    report_generator.open_board_file(BOARD_FILE_NAME)
    config = {ConfigAttributes.REQUIREMENTS: [RequirementTypes.DRAW_BOARD,
                                              RequirementTypes.DRAW_BOARD_WITH_PINS,
                                              RequirementTypes.DRAW_IVC,
                                              RequirementTypes.DRAW_PINS]}
    report_generator.run(config)
