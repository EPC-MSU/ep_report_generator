"""
File with class to generate report.
"""

import logging
import os
import platform
import shutil
import webbrowser
from datetime import datetime, timedelta
from enum import auto, Enum
from typing import Callable, Dict, List, Optional, Tuple
from PyQt5.QtCore import pyqtSignal, QObject
from epcore.elements import Board
from epcore.measurementmanager import IVCComparator
from . import utils as ut
from .version import Version

logger = logging.getLogger(__name__)
_BOARD_IMAGE = "board_clear.png"
_BOARD_WITH_BAD_PINS_IMAGE = "board_with_bad_pins.png"
_BOARD_WITH_PINS_IMAGE = "board.png"
_SCORE_HISTOGRAM_IMAGE = "score_histogram.png"
_DEFAULT_REPORT_DIR_NAME = "report"
_IMG_DIR_NAME = "img"
_STATIC_DIR_NAME = "static"
_STYLE_FOR_MAP = "style_for_map.css"
_STYLE_FOR_REPORT = "style_for_report.css"
_STYLES_DIR_NAME = "styles"
_TEMPLATE_FILE_WITH_FULL_REPORT = "report_full.html"
_TEMPLATE_FILE_WITH_FULL_REPORT_EN = "report_full_en.html"
_TEMPLATE_FILE_WITH_MAP = "full_img.html"
_TEMPLATE_FILE_WITH_MAP_EN = "full_img_en.html"
_TEMPLATE_FILE_WITH_REPORT = "report.html"
_TEMPLATE_FILE_WITH_REPORT_EN = "report_en.html"
_TEMPLATES_DIR_NAME = "report_templates"
_PIN_RADIUS = 6
_PIN_WIDTH = 100


class ConfigAttributes(Enum):
    """
    Attributes in config directory.
    """

    APP_NAME = auto()
    APP_VERSION = auto()
    BOARD_REF = auto()
    BOARD_TEST = auto()
    DIRECTORY = auto()
    ENGLISH = auto()
    OBJECTS = auto()
    OPEN_REPORT_AT_FINISH = auto()
    PIN_SIZE = auto()
    REPORTS_TO_OPEN = auto()
    SCALING_TYPE = auto()
    TEST_DURATION = auto()
    THRESHOLD_SCORE = auto()
    USER_DEFINED_SCALES = auto()


class ObjectsForReport(Enum):
    """
    Objects for which report should be created.
    """

    BOARD = auto()
    ELEMENT = auto()
    PIN = auto()


class ReportCreationSteps(Enum):
    """
    Stages of creating report.
    """

    DRAW_BOARD = auto()
    DRAW_BOARD_WITH_BAD_PINS = auto()
    DRAW_CLEAR_BOARD = auto()
    DRAW_IV = auto()
    DRAW_PINS = auto()
    DRAW_SCORE_HISTOGRAM = auto()
    CREATE_MAP_REPORT = auto()
    CREATE_REPORT = auto()

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


class ReportTypes(Enum):
    """
    Types of report.
    """

    FULL_REPORT = auto()
    MAP_REPORT = auto()
    SHORT_REPORT = auto()


def check_stop_operation(func: Callable):
    """
    Decorator checks if operation needs to be stopped.
    :param func: decorated method.
    """

    def wrapper(self, *args):
        if self.stop:
            return
        return func(self, *args)
    return wrapper


class ReportGenerator(QObject):
    """
    Class to generate report for Board object.
    """

    exception_raised = pyqtSignal(str)
    generation_finished = pyqtSignal(str)
    generation_stopped = pyqtSignal()
    step_done = pyqtSignal()
    step_started = pyqtSignal(str)
    total_number_of_steps_calculated = pyqtSignal(int)

    def __init__(self, parent=None, board_test: Optional[Board] = None, board_ref: Optional[Board] = None,
                 config: Optional[Dict] = None):
        """
        :param parent: parent object;
        :param board_test: test board for which report should be generated;
        :param board_ref: reference board;
        :param config: dictionary with full information about required report.
        """

        super().__init__(parent=parent)
        self._app_name: str = None
        self._app_version: str = None
        self._bad_pins_info: List = []
        self._board: Board = None
        self._board_ref: Board = board_ref
        self._board_test: Board = board_test
        self._config: Dict = config
        self._dir_name: str = self._get_default_dir_name()
        self._english: bool = False
        self._open_report_at_finish: bool = False
        self._pin_diameter: int = None
        self._pin_width: int = _PIN_WIDTH
        self._pins_info: List = []
        self._reports_to_open: List = []
        self._required_board: bool = False
        self._required_elements: List = []
        self._required_pins: List = []
        self._results_by_steps: Dict = ReportCreationSteps.get_dict()
        self._scaling_type: ut.ScalingTypes = ut.ScalingTypes.AUTO
        self._static_dir_name: str = None
        self._test_duration: timedelta = None
        self._threshold_score: float = None
        self._user_defined_scales: list = None
        self.stop: bool = False

    @check_stop_operation
    def _create_full_report(self) -> str:
        """
        Method creates full report.
        :return: name of file with created report.
        """

        self.step_started.emit("Creation of full report")
        logger.info("Creation of full report was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_FULL_REPORT)
        if self._english:
            template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_FULL_REPORT_EN)
        else:
            template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_FULL_REPORT)
        style_file = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _STYLE_FOR_REPORT)
        shutil.copyfile(style_file, os.path.join(self._static_dir_name, _STYLES_DIR_NAME, _STYLE_FOR_REPORT))
        elements_number = len({pin_info[1] for pin_info in self._pins_info})
        if self._board.image is None:
            board_image_width = None
            pin_img_size = None
        else:
            board_image_width = self._board.image.width
            pin_img_size = self._pin_width
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
        data = {"pcb_name": pcb_name,
                "pcb_comment": pcb_comment,
                "mm_per_px": mm_per_px,
                "elements_number": elements_number,
                "board_img_width": board_image_width,
                "pin_img_size": pin_img_size}
        data.update(self._get_general_info())
        ut.create_report(template_file_name, report_file_name, **data)
        self.step_done.emit()
        logger.info("Full report was saved to '%s'", report_file_name)
        return report_file_name

    @check_stop_operation
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

    @check_stop_operation
    def _create_report(self) -> str:
        """
        Method creates short report. This report contains pins that do not match.
        :return: name of file with created report.
        """

        self.step_started.emit("Creation of report")
        logger.info("Creation of report was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_REPORT)
        if self._english:
            template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_REPORT_EN)
        else:
            template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_REPORT)
        style_file = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _STYLE_FOR_REPORT)
        shutil.copyfile(style_file, os.path.join(self._static_dir_name, _STYLES_DIR_NAME, _STYLE_FOR_REPORT))
        elements_number = len({pin_info[1] for pin_info in self._pins_info})
        if self._board.image is None:
            board_image_width = None
            pin_img_size = None
        else:
            board_image_width = self._board.image.width
            pin_img_size = self._pin_width
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
        data = {"pcb_name": pcb_name,
                "pcb_comment": pcb_comment,
                "mm_per_px": mm_per_px,
                "elements_number": elements_number,
                "board_img_width": board_image_width,
                "pin_img_size": pin_img_size}
        data.update(self._get_general_info())
        data.update(self._get_info_about_bad_elements_and_pins())
        ut.create_report(template_file_name, report_file_name, **data)
        self.step_done.emit()
        self.generation_finished.emit(os.path.dirname(report_file_name))
        logger.info("Report was saved to '%s'", report_file_name)
        return report_file_name

    @check_stop_operation
    def _create_report_with_map(self) -> Optional[str]:
        """
        Method creates report with one big image of board.
        :return: name of file with created report.
        """

        if not self._results_by_steps[ReportCreationSteps.DRAW_BOARD]:
            self.step_done.emit()
            return
        self.step_started.emit("Creation of report with board map")
        logger.info("Creation of report with board map was started")
        dir_name = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_MAP)
        if self._english:
            template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_MAP_EN)
        else:
            template_file_name = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _TEMPLATE_FILE_WITH_MAP)
        style_file = os.path.join(dir_name, _TEMPLATES_DIR_NAME, _STYLE_FOR_MAP)
        shutil.copyfile(style_file, os.path.join(self._static_dir_name, _STYLES_DIR_NAME, _STYLE_FOR_MAP))
        ut.create_report(template_file_name, report_file_name, pins=self._pins_info)
        self.step_done.emit()
        logger.info("Report with board map was saved to '%s'", report_file_name)
        return report_file_name

    @check_stop_operation
    def _draw_board(self) -> bool:
        """
        Method draws and saves board image without pins.
        :return: True if image was drawn and saved.
        """

        self.step_started.emit("Drawing of board")
        logger.info("Drawing of board was started")
        file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, _BOARD_IMAGE)
        if self._board.image:
            self._board.image.save(file_name)
            self.step_done.emit()
            logger.info("Image of board was saved to '%s'", file_name)
            return True
        self.step_done.emit()
        logger.info("Image of board was not drawn")
        return False

    @check_stop_operation
    def _draw_board_with_pins(self, bad_pins: bool = False) -> bool:
        """
        Method draws and saves image of board with pins.
        :param bad_pins: if True then board will be drawn with only bad pins.
        :return: True if image was drawn and saved.
        """

        if bad_pins:
            pins_name = "bad pins"
            board_file_name = _BOARD_WITH_BAD_PINS_IMAGE
            pins = self._bad_pins_info
        else:
            pins_name = "pins"
            board_file_name = _BOARD_WITH_PINS_IMAGE
            pins = self._pins_info
        self.step_started.emit(f"Drawing of board with {pins_name}")
        logger.info("Drawing of board with %s was started", pins_name)
        self._pin_diameter = self._get_pin_diameter()
        file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, board_file_name)
        if ut.draw_board_with_pins(self._board.image, pins, file_name, self._pin_diameter):
            self.step_done.emit()
            logger.info("Image of board with %s was saved to '%s'", pins_name, file_name)
            return True
        self.step_done.emit()
        logger.info("Image of board with %s was not drawn", pins_name)
        return False

    @check_stop_operation
    def _draw_ivc(self) -> bool:
        """
        Method draws IV-curves for pins and saves them.
        :return: True if images were drawn and saved.
        """

        self.step_started.emit("Drawing of IV-curves")
        logger.info("Drawing of IV-curves was started")
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        ut.draw_ivc_for_pins(self._pins_info, img_dir_path, self.step_done, self._scaling_type, self._english,
                             lambda: self.stop, self._user_defined_scales)
        logger.info("Images of IV-curves were saved to directory '%s'", img_dir_path)
        return True

    @check_stop_operation
    def _draw_score_histogram(self) -> bool:
        """
        Method draws histogram for scores of pins.
        :return: True if histogram was drawn and saved.
        """

        self.step_started.emit("Drawing of score histogram")
        logger.info("Drawing of score histogram was started")
        all_scores = [pin_info[6] for pin_info in self._pins_info if pin_info[6] is not None]
        if all_scores:
            img_name = os.path.join(self._static_dir_name, _SCORE_HISTOGRAM_IMAGE)
            ut.draw_score_histogram(all_scores, self._threshold_score, img_name)
            self.step_done.emit()
            logger.info("Score histogram was saved to '%s'", img_name)
            return True
        self.step_done.emit()
        logger.info("Score histogram was not drawn")
        return False

    @check_stop_operation
    def _draw_pins(self) -> bool:
        """
        Method draws pins images and saves them.
        :return: True if images were drawn and saved.
        """

        self.step_started.emit("Drawing of pins")
        logger.info("Drawing of pins was started")
        img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
        if ut.draw_pins(self._board.image, self._pins_info, img_dir_path, self.step_done, self._pin_width,
                        lambda: self.stop):
            logger.info("Images of pins were saved to directory '%s'", img_dir_path)
            return True
        for _ in range(len(self._pins_info)):
            self.step_done.emit()
        logger.info("Images of pins were not drawn")
        return False

    def _get_bad_pins(self) -> List:
        """
        Method returns bad pins with score greater than threshold score.
        :return: list with bad pins.
        """

        bad_pins = []
        if self._threshold_score is not None:
            for pin_info in self._pins_info:
                _, _, _, _, _, _, score, _, _, _, _ = pin_info
                if score is not None and score > self._threshold_score:
                    bad_pins.append(pin_info)
        return bad_pins

    @staticmethod
    def _get_default_dir_name() -> str:
        """
        Method returns default name for directory where report will be saved.
        :return: default name for directory.
        """

        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def _get_general_info(self) -> Dict:
        """
        Method returns dictionary with general information.
        :return: dictionary with general information.
        """

        return {"date": datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
                "app_name": self._app_name,
                "app_version": self._app_version,
                "computer": os.environ.get("COMPUTERNAME", "Unknown"),
                "operating_system": f"{platform.system()} {platform.release()} {platform.architecture()[0]}",
                "test_duration": self._test_duration,
                "pins": self._pins_info,
                "pins_number": len(self._pins_info),
                "threshold_score": self._threshold_score,
                "score_histogram": self._results_by_steps[ReportCreationSteps.DRAW_SCORE_HISTOGRAM],
                "pin_radius": _PIN_RADIUS if self._pin_diameter is None else int(self._pin_diameter / 2)}

    def _get_info_about_bad_elements_and_pins(self) -> Dict:
        """
        Method returns dictionary with information about bad elements and pins.
        Bad pin is pin with score greater than threshold score. Bad element has
        at least one bad pin.
        :return: dictionary with information about bad elements and pins.
        """

        bad_element_names = set()
        for pin_info in self._bad_pins_info:
            element_name, _, _, _, _, _, score, _, _, _, _ = pin_info
            bad_element_names.add(element_name)
        return {"bad_elements_number": len(bad_element_names),
                "bad_pins_number": len(self._bad_pins_info),
                "bad_pins": self._bad_pins_info}

    @check_stop_operation
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
                        score = comparator.compare_ivc(pin.measurements[0].ivc, pin.measurements[1].ivc)
                    else:
                        score = None
                    pin_type = ut.get_pin_type(score, self._threshold_score)
                    info = (element.name, element_index, pin_index, pin.x, pin.y, pin.measurements, score,
                            pin_type, total_pin_index, pin.comment, pin.multiplexer_output)
                    pins_info.append(info)
                total_pin_index += 1
        pin_number = len(pins_info)
        self.total_number_of_steps_calculated.emit(self._get_total_number_of_steps(pin_number))
        return pins_info

    @check_stop_operation
    def _get_pin_diameter(self) -> Optional[int]:
        """
        Method determines diameter of pins on image of board with pins.
        :return: diameter of pins.
        """

        if not self._board.image:
            return None
        # min_distance = ut.calculate_min_distance(self._pins_info)
        # logger.info("Minimum distance between pins was calculated: %s", min_distance)
        # pin_diameter = min(self._board.image.width // 38, int(min_distance))
        # logger.info("Pin size on image of board with pins is %s", pin_diameter)
        pin_diameter = self._board.image.width // 38
        return pin_diameter

    def _get_total_number_of_steps(self, pin_number: int) -> int:
        """
        Method returns total number of steps to generate all reports.
        :param pin_number: number of pins on board.
        :return: total number of steps.
        """

        processes = (self._draw_board, self._draw_board_with_pins, self._draw_board_with_pins,
                     self._draw_score_histogram, self._create_report_with_map, self._create_full_report,
                     self._create_report_with_map)
        processes_for_pins = self._draw_pins, self._draw_ivc
        return len(processes) + len(processes_for_pins) * pin_number

    @check_stop_operation
    def _read_config(self, config: Dict):
        """
        Method reads dictionary with full information about required report.
        :param config: dictionary with full information about required report.
        """

        if not isinstance(config, Dict) and not isinstance(self._config, Dict):
            config = {ConfigAttributes.APP_NAME: None,
                      ConfigAttributes.APP_VERSION: None,
                      ConfigAttributes.BOARD_REF: self._board_ref,
                      ConfigAttributes.BOARD_TEST: self._board_test,
                      ConfigAttributes.DIRECTORY: self._dir_name,
                      ConfigAttributes.ENGLISH: False,
                      ConfigAttributes.OBJECTS: {},
                      ConfigAttributes.OPEN_REPORT_AT_FINISH: False,
                      ConfigAttributes.PIN_SIZE: _PIN_WIDTH,
                      ConfigAttributes.REPORTS_TO_OPEN: [ReportTypes.SHORT_REPORT],
                      ConfigAttributes.SCALING_TYPE: ut.ScalingTypes.AUTO,
                      ConfigAttributes.TEST_DURATION: None,
                      ConfigAttributes.THRESHOLD_SCORE: None,
                      ConfigAttributes.USER_DEFINED_SCALES: None}
        elif not isinstance(config, Dict) and isinstance(self._config, Dict):
            config = self._config
        self._config = config
        self._app_name = self._config.get(ConfigAttributes.APP_NAME, None)
        self._app_version = self._config.get(ConfigAttributes.APP_VERSION, None)
        self._board_ref = self._config.get(ConfigAttributes.BOARD_REF, self._board_ref)
        self._board_test = self._config.get(ConfigAttributes.BOARD_TEST, self._board_test)
        parent_directory = self._config.get(ConfigAttributes.DIRECTORY, self._dir_name)
        self._dir_name = ut.create_report_directory_name(parent_directory, _DEFAULT_REPORT_DIR_NAME)
        self._english = self._config.get(ConfigAttributes.ENGLISH, False)
        self._open_report_at_finish = self._config.get(ConfigAttributes.OPEN_REPORT_AT_FINISH, False)
        self._pin_width = self._config.get(ConfigAttributes.PIN_SIZE, _PIN_WIDTH)
        self._reports_to_open = list(set(self._config.get(ConfigAttributes.REPORTS_TO_OPEN,
                                                          [ReportTypes.SHORT_REPORT])))
        self._scaling_type = self._config.get(ConfigAttributes.SCALING_TYPE, ut.ScalingTypes.AUTO)
        self._test_duration = self._config.get(ConfigAttributes.TEST_DURATION, None)
        self._test_duration = ut.get_duration_in_str(self._test_duration, self._english)
        self._threshold_score = self._config.get(ConfigAttributes.THRESHOLD_SCORE, None)
        self._user_defined_scales = self._config.get(ConfigAttributes.USER_DEFINED_SCALES, None)
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
        self._bad_pins_info = self._get_bad_pins()
        if not self._pins_info:
            logger.info("There are no objects for which report should be created")
            return
        methods = {ReportCreationSteps.DRAW_CLEAR_BOARD: self._draw_board,
                   ReportCreationSteps.DRAW_BOARD: self._draw_board_with_pins,
                   ReportCreationSteps.DRAW_BOARD_WITH_BAD_PINS: (lambda: self._draw_board_with_pins(True)),
                   ReportCreationSteps.DRAW_SCORE_HISTOGRAM: self._draw_score_histogram,
                   ReportCreationSteps.DRAW_IV: self._draw_ivc,
                   ReportCreationSteps.DRAW_PINS: self._draw_pins}
        for step, method in methods.items():
            self._results_by_steps[step] = method()
        created_reports = {ReportTypes.MAP_REPORT: self._create_report_with_map(),
                           ReportTypes.FULL_REPORT: self._create_full_report(),
                           ReportTypes.SHORT_REPORT: self._create_report()}
        if self._open_report_at_finish:
            for report_to_open in self._reports_to_open:
                report_file_name = created_reports.get(report_to_open, None)
                if report_file_name:
                    webbrowser.open(report_file_name, new=2)

    @classmethod
    def get_version(cls) -> str:
        """
        Method returns version of package.
        :return: version.
        """

        return Version.full

    def run(self, config: Dict):
        """
        Method runs report generation.
        :param config: dictionary with full information about required report.
        """

        self._read_config(config)
        try:
            self._run()
            if self.stop:
                self.generation_stopped.emit()
        except Exception as exc:
            exception_text = f"Error occurred while generating report: {exc}"
            self.exception_raised.emit(exception_text)
            logger.error(exception_text)

    def stop_process(self):
        """
        Method stops generation of report.
        """

        logger.info("Generation of report was stopped")
        self.stop = True
