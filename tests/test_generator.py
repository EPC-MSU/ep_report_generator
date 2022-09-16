import logging
import os
import sys
import unittest
from PyQt5.QtWidgets import QApplication
from report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator
from tests.utils import create_simple_board


logger = logging.getLogger("report_generator")
logger.setLevel(logging.ERROR)


class TestGenerator(unittest.TestCase):

    def test_simple_report(self) -> None:

        def check_reports_creation(dir_name: str) -> None:
            required_files = "report.html", "report_full.html"
            required_dir = "static"
            for file_or_dir in os.listdir(dir_name):
                if os.path.isdir(os.path.join(dir_name, file_or_dir)):
                    self.assertEqual(file_or_dir, required_dir)
                elif os.path.isfile(os.path.join(dir_name, file_or_dir)):
                    self.assertIn(file_or_dir, required_files)
                else:
                    self.assertTrue(False)

        app = QApplication(sys.argv)
        app.some_action_to_fix_flake8 = True
        dir_for_report = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "test_report")
        config = {ConfigAttributes.BOARD: create_simple_board(),
                  ConfigAttributes.DIRECTORY: dir_for_report,
                  ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                             ObjectsForReport.ELEMENT: [],
                                             ObjectsForReport.PIN: []},
                  ConfigAttributes.THRESHOLD_SCORE: 0.2,
                  ConfigAttributes.OPEN_REPORT_AT_FINISH: False}
        report_generator = ReportGenerator()
        report_generator.generation_finished.connect(check_reports_creation)
        report_generator.run(config)

        self.assertTrue(os.path.exists(dir_for_report))
