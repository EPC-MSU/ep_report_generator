"""
File with class to generate report.
"""

import logging
import os
import shutil
from enum import Enum
from typing import Dict, List, Optional, Tuple
from PyQt5.QtCore import pyqtSignal, QObject
from epcore.elements import Board
from epcore.filemanager import load_board_from_ufiv
from epcore.measurementmanager import IVCComparator
from . import utils as ut
from .version import Version

logger = logging.getLogger(__name__)
_BOARD_IMAGE = "board_clear.png"
_BOARD_WITH_PINS_IMAGE = "board.png"
_DEFAULT_REPORT_DIR_NAME = "board_report"
_IMG_DIR_NAME = "img"
_STATIC_DIR_NAME = "static"
_STYLE_FOR_MAP = "style_for_map.css"
_STYLE_FOR_REPORT = "style_for_report.css"
_STYLES_DIR_NAME = "styles"
_TEMPLATE_FILE_WITH_MAP = "map.html"
_TEMPLATE_FILE_WITH_REPORT = "report.html"
_TEMPLATES_DIR_NAME = "report_templates"


class ConfigAttributes(Enum):
    """
    Attributes in config directory.
    """

    BOARD_TEST = 0
    BOARD_REF = 1
    DIRECTORY = 2
    OBJECTS = 3
    THRESHOLD_SCORE = 4


class ObjectsForReport(Enum):
    """
    Objects for which report should be created.
    """

    BOARD = 0
    ELEMENT = 1
    PIN = 2


class ReportCreationSteps(Enum):
    """
    Stages of creating report.
    """

    DRAW_BOARD = 0
    DRAW_IV = 1
    DRAW_PINS = 2
    CREATE_MAP_REPORT = 3
    CREATE_REPORT = 4

    @classmethod
    def get_dict(cls) -> Dict:
        """
        Method returns dictionary for results by stages of report creation.
        :return: dictionary for results by stages.
        """

        return {cls.DRAW_BOARD: None,
                cls.DRAW_IV: None,
                cls.DRAW_PINS: None,
                cls.CREATE_MAP_REPORT: None,
                cls.CREATE_REPORT: None}


class ReportGenerator(QObject):
    """
    Class to generate report for Board object.
    """

    exception_raised = pyqtSignal(str)
    generation_finished = pyqtSignal(str)
    step_done = pyqtSignal()
    step_started = pyqtSignal(str)
    total_number_of_steps_calculated = pyqtSignal(int)

    def __init__(self, parent=None, board_test: Optional[Board] = None,
                 board_ref: Optional[Board] = None, config: Optional[Dict] = None):
        """
        :param parent: parent object;
        :param board_test: test board for which report should be generated;
        :param board_ref: reference board;
        :param config: dictionary with full information about required report.
        """

        super().__init__(parent=parent)
        self._board: Board = None
        self._board_ref: Board = board_ref
        self._board_test: Board = board_test
        self._config: Dict = config
        self._dir_name: str = self._get_default_dir_name()
        self._pins_info: List = []
        self._required_board: bool = False
        self._required_elements: List = []
        self._required_pins: List = []
        self._results_by_steps: Dict = ReportCreationSteps.get_dict()
        self._static_dir_name: str = None
        self._threshold_score: float = None

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

    def _create_report_with_map(self):
        """
        Method creates report with one big image of board.
        """

        if not self._results_by_steps[ReportCreationSteps.DRAW_BOARD]:
            self.step_done.emit()
            return
        self.step_started.emit("Creation of report with board map")
        logger.info("Creation of report with board map was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_MAP)
        template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME,
                                          _TEMPLATE_FILE_WITH_MAP)
        style_file = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _STYLE_FOR_MAP)
        shutil.copyfile(style_file, os.path.join(self._static_dir_name, _STYLES_DIR_NAME,
                                                 _STYLE_FOR_MAP))
        ut.create_report(template_file_name, report_file_name, pins=self._pins_info)
        self.step_done.emit()
        logger.info("Report with board map was saved to '%s'", report_file_name)

    def _create_report(self):
        """
        Method creates report.
        """

        self.step_started.emit("Creation of report")
        logger.info("Creation of report was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_REPORT)
        template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_REPORT)
        style_file = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _STYLE_FOR_REPORT)
        shutil.copyfile(style_file, os.path.join(self._static_dir_name, _STYLES_DIR_NAME,
                                                 _STYLE_FOR_REPORT))
        elements_number = len({pin_info[1] for pin_info in self._pins_info})
        if self._board.image is None:
            board_image_width = None
            pin_img_size = None
        else:
            board_image_width = self._board.image.width
            pin_img_size = 2 * ut.PIN_HALF_WIDTH
        pcb_name = None
        pcb_comment = None
        mm_per_px = None
        if self._board.pcb is not None:
            if self._board.pcb.pcb_name is not None:
                pcb_name = self._board.pcb.pcb_name
            if self._board.pcb.comment is not None:
                pcb_comment = self._board.pcb.comment
            if self._board.pcb.image_resolution_ppcm is not None:
                mm_per_px = 10 / self._board.pcb.image_resolution_ppcm
        data = {"pins": self._pins_info,
                "pcb_name": pcb_name,
                "pcb_comment": pcb_comment,
                "mm_per_px": mm_per_px,
                "elements_number": elements_number,
                "pins_number": len(self._pins_info),
                "board_img_width": board_image_width,
                "pin_img_size": pin_img_size,
                "threshold_score": self._threshold_score}
        ut.create_report(template_file_name, report_file_name, **data)
        self.step_done.emit()
        self.generation_finished.emit(report_file_name)
        logger.info("Report was saved to '%s'", report_file_name)

    def _draw_board(self):
        """
        Method draws and saves board image without pins.
        """

        self.step_started.emit("Drawing of board")
        logger.info("Board drawing was started")
        file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, _BOARD_IMAGE)
        self._board.image.save(file_name)
        logger.info("Board image was saved to '%s'", file_name)

    def _draw_board_with_pins(self) -> bool:
        """
        Method draws and saves image of board with pins.
        :return: True if image was drawn and saved.
        """

        self.step_started.emit("Drawing of board with pins")
        logger.info("Drawing of board with pins was started")
        file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, _BOARD_WITH_PINS_IMAGE)
        if ut.draw_board_with_pins(self._board.image, self._pins_info, file_name):
            self.step_done.emit()
            logger.info("Image of board with pins was saved to '%s'", file_name)
            return True
        self.step_done.emit()
        logger.info("Image of board with pins was not drawn")
        return False

    def _draw_ivc(self) -> bool:
        """
        Method draws IV-curves for pins and saves them.
        :return: True if images were drawn and saved.
        """

        self.step_started.emit("Drawing of IV-curves")
        logger.info("Drawing of IV-curves was started")
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        ut.draw_ivc_for_pins(self._pins_info, img_dir_path, self.step_done)
        logger.info("Images of IV-curves were saved to directory '%s'", img_dir_path)
        return True

    def _draw_pins(self) -> bool:
        """
        Method draws pins images and saves them.
        :return: True if images were drawn and saved.
        """

        self.step_started.emit("Drawing of pins")
        logger.info("Drawing of pins was started")
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        if ut.draw_pins(self._board.image, self._pins_info, img_dir_path, self.step_done):
            logger.info("Images of pins were saved to directory '%s'", img_dir_path)
            return True
        for _ in range(len(self._pins_info)):
            self.step_done.emit()
        logger.info("Images of pins were not drawn")
        return False

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
        Method returns list with information about pins for which report should
        be generated.
        :return: list with information about required pins.
        """

        self._board = ut.create_board(self._board_test, self._board_ref)
        comparator = IVCComparator()
        comparator.set_min_ivc(0, 0)
        pins_info = []
        total_pin_index = 0
        for element_index, element in enumerate(self._board.elements):
            for pin_index, pin in enumerate(element.pins):
                if (self._required_board or element_index in self._required_elements or
                        total_pin_index in self._required_pins):
                    if len(pin.measurements) > 1:
                        score = comparator.compare_ivc(pin.measurements[0].ivc,
                                                       pin.measurements[1].ivc)
                    else:
                        score = None
                    pin_type = ut.get_pin_type(pin.measurements, score, self._threshold_score)
                    info = (element.name, element_index, pin_index, pin.x, pin.y, pin.measurements,
                            score, pin_type, total_pin_index, pin.comment)
                    pins_info.append(info)
                total_pin_index += 1
        pin_number = len(pins_info)
        self.total_number_of_steps_calculated.emit(3 + pin_number * 2)
        return pins_info

    def _read_config(self, config: Dict):
        """
        Method reads dictionary with full information about required report.
        :param config: dictionary with full information about required report.
        """

        if not isinstance(config, Dict) and not isinstance(self._config, Dict):
            config = {ConfigAttributes.BOARD_TEST: self._board_test,
                      ConfigAttributes.BOARD_REF: self._board_ref,
                      ConfigAttributes.DIRECTORY: self._dir_name,
                      ConfigAttributes.OBJECTS: {},
                      ConfigAttributes.THRESHOLD_SCORE: None}
        elif isinstance(self._config, Dict):
            config = self._config
        self._config = config
        self._board_ref = self._config.get(ConfigAttributes.BOARD_REF, self._board_ref)
        self._board_test = self._config.get(ConfigAttributes.BOARD_TEST, self._board_test)
        self._dir_name = self._config.get(ConfigAttributes.DIRECTORY, self._dir_name)
        self._threshold_score = self._config.get(ConfigAttributes.THRESHOLD_SCORE,
                                                 self._threshold_score)
        required_objects = self._config.get(ConfigAttributes.OBJECTS, {})
        if required_objects.get(ObjectsForReport.BOARD):
            self._required_board = True
        else:
            self._required_elements = required_objects.get(ObjectsForReport.ELEMENT)
            self._required_pins = required_objects.get(ObjectsForReport.PIN)

    def _run(self):
        """
        Method runs report generation.
        """

        if not isinstance(self._board_test, Board) and isinstance(self._board_ref, Board):
            return
        self._create_required_dirs()
        self._pins_info = self._get_info_about_pins()
        if not self._pins_info:
            logger.info("There are no objects for which report should be created")
            return
        methods = {ReportCreationSteps.DRAW_BOARD: self._draw_board_with_pins,
                   ReportCreationSteps.DRAW_IV: self._draw_ivc,
                   ReportCreationSteps.DRAW_PINS: self._draw_pins}
        for step, method in methods.items():
            self._results_by_steps[step] = method()
        self._create_report_with_map()
        self._create_report()

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
        self._board_test = board
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
            exception_text = f"Error occurred while generating report: {exc}"
            self.exception_raised.emit(exception_text)
            logger.error(exception_text)
