import logging
import os
import sys
import unittest
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QApplication
from epcore.elements import Board
from report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator
from tests.utils import create_simple_board, read_file


logger = logging.getLogger("report_generator")
logger.setLevel(logging.ERROR)


class TestGenerator(unittest.TestCase):

    empty_report_dir: str = None
    simple_report_dir: str = None

    @classmethod
    def setUpClass(cls) -> None:
        cls._app: QApplication = QApplication(sys.argv[1:])
        cls._app.some_action_to_fix_flake8 = True
        cls._dir_for_report: str = os.path.join(os.path.curdir, "test_report")

        # Generate empty report
        report_generator = ReportGenerator()
        report_generator.generation_finished.connect(cls._save_empty_report_dir)
        config = {ConfigAttributes.BOARD: Board(),
                  ConfigAttributes.DIRECTORY: cls._dir_for_report,
                  ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True}}
        report_generator.run(config)

        # Generate simple report
        try:
            report_generator.generation_finished.disconnect()
        except Exception:
            pass
        report_generator.generation_finished.connect(cls._save_simple_report_dir)
        config = {ConfigAttributes.BOARD: create_simple_board(),
                  ConfigAttributes.DIRECTORY: cls._dir_for_report,
                  ConfigAttributes.OBJECTS: {ObjectsForReport.BOARD: True,
                                             ObjectsForReport.ELEMENT: [],
                                             ObjectsForReport.PIN: []},
                  ConfigAttributes.OPEN_REPORT_AT_FINISH: False,
                  ConfigAttributes.TOLERANCE: 0.2}
        report_generator.run(config)

    def _check_reports_creation(self, dir_name: str) -> None:
        required_files = "report.html", "report_full.html"
        required_dir = "static"
        for file_or_dir in os.listdir(dir_name):
            if os.path.isdir(os.path.join(dir_name, file_or_dir)):
                self.assertEqual(file_or_dir, required_dir)
            elif os.path.isfile(os.path.join(dir_name, file_or_dir)):
                self.assertIn(file_or_dir, required_files)
            else:
                self.assertTrue(False)

    @classmethod
    def _save_empty_report_dir(cls, dir_name: str) -> None:
        cls.empty_report_dir = dir_name

    @classmethod
    def _save_simple_report_dir(cls, dir_name: str) -> None:
        cls.simple_report_dir = dir_name

    def test_empty_report(self) -> None:
        report_file = os.path.join(TestGenerator.empty_report_dir, "report.html")
        soup = BeautifulSoup(read_file(report_file), "html.parser")
        self.assertEqual(soup.find("h1").text.strip(), "Отчет")
        self.assertEqual(len(soup.find_all("td", {"class": "element_name"})), 0)
        self.assertEqual(len(soup.find_all("a", {"class": "anchor"})), 0)

    def test_empty_full_report(self) -> None:
        report_file = os.path.join(TestGenerator.empty_report_dir, "report_full.html")
        soup = BeautifulSoup(read_file(report_file), "html.parser")
        self.assertEqual(soup.find("h1").text.strip(), "Полный отчет")
        self.assertEqual(len(soup.find_all("td", {"class": "element_name"})), 0)
        self.assertEqual(len(soup.find_all("a", {"class": "anchor"})), 0)

    def test_empty_report_generation(self) -> None:
        self.assertIsNotNone(TestGenerator.empty_report_dir)
        self.assertTrue(os.path.exists(TestGenerator.empty_report_dir))
        self._check_reports_creation(TestGenerator.empty_report_dir)

    def test_simple_report(self) -> None:
        report_file = os.path.join(TestGenerator.simple_report_dir, "report.html")
        soup = BeautifulSoup(read_file(report_file), "html.parser")
        self.assertEqual(soup.find("h1").text.strip(), "Отчет")
        self.assertEqual(len(soup.find_all("td", {"class": "element_name"})), 0)
        self.assertEqual(len(soup.find_all("a", {"class": "anchor"})), 0)

    def test_simple_full_report(self) -> None:
        report_file = os.path.join(TestGenerator.simple_report_dir, "report_full.html")
        soup = BeautifulSoup(read_file(report_file), "html.parser")
        self.assertEqual(soup.find("h1").text.strip(), "Полный отчет")
        self.assertEqual(len(soup.find_all("td", {"class": "element_name"})), 1)
        self.assertEqual(len(soup.find_all("a", {"class": "anchor"})), 3)

    def test_simple_report_generation(self) -> None:
        self.assertIsNotNone(TestGenerator.simple_report_dir)
        self.assertTrue(os.path.exists(TestGenerator.simple_report_dir))
        self._check_reports_creation(TestGenerator.simple_report_dir)
