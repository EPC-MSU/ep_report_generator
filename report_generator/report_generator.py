"""
File with class to generate report.
"""

import logging
import os
from enum import Enum
from typing import Dict, List, Tuple
from PyQt5.QtCore import QThread
from epcore.elements import Board
from epcore.filemanager import load_board_from_ufiv
from . import utils as ut
from .version import Version

logger = logging.getLogger(__name__)
_BOARD_IMAGE = "board_clear.png"
_BOARD_WITH_PINS_IMAGE = "board.png"
_DEFAULT_REPORT_DIR_NAME = "board_report"
_IMG_DIR_NAME = "img"
_STATIC_DIR_NAME = "static"
_STYLES_DIR_NAME = "styles"
_TEMPLATE_FILE_WITH_FULL_IMAGE = "full_img.html"
_TEMPLATE_FILE_WITH_REPORT = "report.html"
_TEMPLATES_DIR_NAME = "report_templates"


class ConfigAttributes(Enum):
    """
    Attributes in config directory.
    """

    BOARD = 0
    DIRECTORY = 1
    REQUIREMENTS = 2


class RequirementTypes(Enum):
    """
    Types of requirements to generate report.
    """

    DRAW_BOARD = 0
    DRAW_BOARD_WITH_PINS = 1
    DRAW_IVC = 2
    DRAW_PINS = 3


class ReportGenerator(QThread):
    """
    Class to generate report for Board object.
    """

    def __init__(self, parent=None, board: Board = None, config: Dict = None):
        """
        :param parent: parent object;
        :param board: board for which report should be generated;
        :param config: dictionary with full information about required report.
        """

        super().__init__(parent=parent)
        self._board: Board = board
        self._config: Dict = config
        self._dir_name: str = self._get_default_dir_name()
        self._requirements: List = []
        self._static_dir_name: str = None

    def _create_required_dirs(self):
        """
        Method checks existence of required folders and creates them if necessary.
        """

        def create_dir(path: str):
            """
            Function creates directory if necessary.
            :param path: path to directory.
            """

            if not os.path.exists(path):
                os.makedirs(path)

        self._static_dir_name = os.path.join(self._dir_name, _STATIC_DIR_NAME)
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        styles_dir_path = os.path.join(self._static_dir_name, _STYLES_DIR_NAME)
        dir_paths = self._dir_name, self._static_dir_name, img_dir_path, styles_dir_path
        for dir_path in dir_paths:
            create_dir(dir_path)

    def _create_report_with_full_image(self, pins_info: List[Tuple]):
        """
        Method creates report with one big image of board.
        :param pins_info: list with information about pins.
        """

        logger.info("Creation of report with full image was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_FULL_IMAGE)
        template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME,
                                          _TEMPLATE_FILE_WITH_FULL_IMAGE)
        ut.create_report(template_file_name, report_file_name, pins=pins_info)
        logger.info("Report with full image was saved to '%s'", report_file_name)

    def _create_report(self, pins_info: List[Tuple]):
        """
        Method creates report.
        :param pins_info: list with information about pins.
        """

        logger.info("Creation of report was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_REPORT)
        template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_REPORT)
        data = {"pins": pins_info,
                "pcb_name": self._board.pcb.pcb_name,
                "mm_per_px": self._board.pcb.image_resolution_ppcm,
                "elements_number": 3,
                "pins_number": len(pins_info),
                "board_img_width": self._board.image.width,
                "pin_img_size": 100}
        ut.create_report(template_file_name, report_file_name, **data)
        logger.info("Report was saved to '%s'", report_file_name)

    def _draw_board(self):
        """
        Method draws and saves board image.
        """

        logger.info("Board drawing was started")
        file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, _BOARD_IMAGE)
        self._board.image.save(file_name)
        logger.info("Board image was saved to '%s'", file_name)

    def _draw_board_with_pins(self):
        """
        Method draws and saves image of board with pins.
        """

        logger.info("Drawing of board with pins was started")
        file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, _BOARD_WITH_PINS_IMAGE)
        ut.draw_board_with_pins(self._board, file_name)
        logger.info("Image of board with pins was saved to '%s'", file_name)

    def _draw_ivc(self):
        """
        Method draws IV-curves for pins and saves them.
        """

        logger.info("Drawing of IV-curves was started")
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        ut.draw_ivc_for_pins(self._board, img_dir_path)
        logger.info("Images of IV-curves were saved to directory '%s'", img_dir_path)

    def _draw_pins(self):
        """
        Method draws pins images and saves them.
        """

        logger.info("Drawing of pins was started")
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        ut.draw_pins(self._board, img_dir_path)
        logger.info("Images of pins were saved to directory '%s'", img_dir_path)

    @staticmethod
    def _get_default_dir_name() -> str:
        """
        Method returns default name for directory where report will be saved.
        :return: default name for directory.
        """

        parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(parent_dir, _DEFAULT_REPORT_DIR_NAME)

    def _get_info_about_pins(self) -> List[Tuple]:
        """
        Method returns list with information about pins.
        :return: list with information about pins.
        """

        pins_info = []
        for element_index, element in enumerate(self._board.elements):
            for pin_index, pin in enumerate(element.pins):
                pins_info.append((element.name, element_index, pin_index, pin.x, pin.y))
        return pins_info

    def _read_config(self, config: Dict):
        """
        Method reads dictionary with full information about required report.
        :param config: dictionary with full information about required report.
        """

        if not isinstance(config, Dict) and not isinstance(self._config, Dict):
            config = {ConfigAttributes.BOARD: self._board,
                      ConfigAttributes.DIRECTORY: self._dir_name,
                      ConfigAttributes.REQUIREMENTS: []}
        elif isinstance(self._config, Dict):
            config = self._config
        self._config = config
        self._board = self._config.get(ConfigAttributes.BOARD, self._board)
        self._dir_name = self._config.get(ConfigAttributes.DIRECTORY, self._dir_name)
        self._requirements = self._config.get(ConfigAttributes.REQUIREMENTS, self._requirements)

    def _run(self):
        """
        Method runs report generation.
        """

        if not isinstance(self._board, Board):
            return
        self._create_required_dirs()
        methods = {RequirementTypes.DRAW_BOARD: self._draw_board,
                   RequirementTypes.DRAW_BOARD_WITH_PINS: self._draw_board_with_pins,
                   RequirementTypes.DRAW_IVC: self._draw_ivc,
                   RequirementTypes.DRAW_PINS: self._draw_pins}
        for requirement, method in methods.items():
            if requirement in self._requirements:
                method()
        pins_info = self._get_info_about_pins()
        self._create_report_with_full_image(pins_info)
        self._create_report(pins_info)

    @classmethod
    def get_version(cls) -> str:
        """
        Method returns version of package.
        :return: version.
        """

        return Version.full

    def open_board_file(self, file_name: str) -> bool:
        """
        Method reads file with board information (in json or uzf format).
        :param file_name: name of file.
        :return: True if file was read otherwise False.
        """

        try:
            board = load_board_from_ufiv(file_name, auto_convert_p10=True)
        except Exception as exc:
            logger.error("File '%s' was not read and board was not created: %s", file_name, exc)
            return False
        self._board = board
        return True

    def run(self, config: Dict):
        """
        Method runs report generation.
        :param config: dictionary with full information about required report.
        """

        self._read_config(config)
        try:
            self._run()
        except Exception as exc:
            logger.error("Error occurred while generating report: %s", exc)
