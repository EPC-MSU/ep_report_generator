"""
File with class to generate report.
"""

import logging
import os
import platform
import shutil
import sys
import webbrowser
from datetime import datetime, timedelta
from enum import auto, Enum
from typing import Any, Dict, List, Optional, Tuple
from PyQt5.QtCore import pyqtSignal, QObject
from epcore.elements import Board
from epcore.measurementmanager import IVCComparator
from report_generator import utils as ut
from report_generator.version import VERSION


logger = logging.getLogger("report_generator")
_BOARD_IMAGE: str = "board_clear.jpeg"
_BOARD_WITH_BAD_PINS_IMAGE: str = "board_with_bad_pins.jpeg"
_BOARD_WITH_PINS_IMAGE: str = "board.jpeg"
_DEFAULT_REPORT_DIR_NAME: str = "report"
_IMG_DIR_NAME: str = "img"
_FAULT_HISTOGRAM_IMAGE: str = "fault_histogram.jpeg"
_SCRIPTS_DIR_NAME: str = "scripts"
_STATIC_DIR_NAME: str = "static"
_STYLES_DIR_NAME: str = "styles"
_TEMPLATE_FILE_WITH_FULL_REPORT: str = "report_full.html"
_TEMPLATE_FILE_WITH_FULL_REPORT_EN: str = "report_full_en.html"
_TEMPLATE_FILE_WITH_MAP: str = "full_img.html"
_TEMPLATE_FILE_WITH_MAP_EN: str = "full_img_en.html"
_TEMPLATE_FILE_WITH_REPORT: str = "report.html"
_TEMPLATE_FILE_WITH_REPORT_EN: str = "report_en.html"
_TEMPLATES_DIR_NAME: str = "report_templates"
_PIN_RADIUS: int = 6
_PIN_WIDTH: int = 100


class ConfigAttributes(Enum):
    """
    Attributes in config directory.
    """

    APP_NAME = auto()
    APP_VERSION = auto()
    BOARD = auto()
    DIRECTORY = auto()
    ENGLISH = auto()
    IS_REPORT_FOR_TEST_BOARD = auto()
    NOISE_AMPLITUDES = auto()
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
    DRAW_FAULT_HISTOGRAM = auto()
    DRAW_IV = auto()
    DRAW_PINS = auto()
    CREATE_MAP_REPORT = auto()
    CREATE_REPORT = auto()

    @classmethod
    def get_dict(cls) -> Dict["ReportCreationSteps", Optional[bool]]:
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


class UserStop(Exception):
    pass


class ReportGenerator(QObject):
    """
    Class to generate report for Board object.
    """

    exception_raised: pyqtSignal = pyqtSignal(str)
    generation_finished: pyqtSignal = pyqtSignal(str)
    generation_stopped: pyqtSignal = pyqtSignal()
    step_done: pyqtSignal = pyqtSignal()
    step_started: pyqtSignal = pyqtSignal(str)
    total_number_of_steps_calculated: pyqtSignal = pyqtSignal(int)

    def __init__(self, parent=None, board: Optional[Board] = None, config: Optional[Dict[ConfigAttributes, Any]] = None
                 ) -> None:
        """
        :param parent: parent object;
        :param board: board for which report should be generated;
        :param config: dictionary with full information about required report.
        """

        super().__init__(parent=parent)
        self._app_name: str = None
        self._app_version: str = None
        self._bad_pins_info: List[ut.PinInfo] = []
        self._board: Board = board
        self._config: Dict[ConfigAttributes, Any] = config
        self._dir_name: str = ut.get_default_dir_path()
        self._dir_template: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                               _TEMPLATES_DIR_NAME)
        self._english: bool = False
        self._is_report_for_test_board: Optional[bool] = None
        self._noise_amplitudes: Optional[List[Optional[Tuple[float, float]]]] = None
        self._open_report_at_finish: bool = False
        self._pin_diameter: int = None
        self._pin_width: int = _PIN_WIDTH
        self._pins_info: List[ut.PinInfo] = []
        self._reports_to_open: List[ReportTypes] = []
        self._required_board: bool = False
        self._required_elements: List[int] = []
        self._required_pins: List[int] = []
        self._results_by_steps: Dict = ReportCreationSteps.get_dict()
        self._scaling_type: ut.ScalingTypes = ut.ScalingTypes.AUTO
        self._static_dir_name: str = None
        self._test_duration: timedelta = None
        self._threshold_score: Optional[float] = None
        self._user_defined_scales: Optional[List[Tuple[float, float]]] = None
        self.stop: bool = False

    def _analyze_required_report_type(self) -> None:
        """
        Method determines the type of report to be generated (for a test board or for a reference board).
        """

        if self._is_report_for_test_board is None:
            self._is_report_for_test_board = False
            for element in self._board.elements:
                self._check_stop_operation()
                for pin in element.pins:
                    self._check_stop_operation()
                    if len(pin.measurements) > 0:
                        for measurement in pin.measurements:
                            if not measurement.is_reference:
                                self._is_report_for_test_board = True
                                break

    def _check_stop_operation(self) -> None:
        if self.stop:
            raise UserStop()

    def _copy_favicon_and_styles(self) -> None:
        """
        Method copies favicons and style files to the directory with generated report.
        """

        self._check_stop_operation()
        files_info = [{"file_names": ["style_for_map.css", "style_for_report.css"],
                       "dir_name": _STYLES_DIR_NAME},
                      {"file_names": ["favicon-16x16.png", "favicon-32x32.png"],
                       "dir_name": _IMG_DIR_NAME},
                      {"file_names": ["full_image_script.js", "report_script.js"],
                       "dir_name": _SCRIPTS_DIR_NAME}]

        for file_info in files_info:
            dir_name = file_info["dir_name"]
            for file_name in file_info["file_names"]:
                self._check_stop_operation()
                file_path = os.path.join(self._dir_template, file_name)
                shutil.copyfile(file_path, os.path.join(self._static_dir_name, dir_name, file_name))

    def _create_required_dirs(self) -> None:
        """
        Method checks for the presence of the required directories and creates them if necessary.
        """

        self._static_dir_name = os.path.join(self._dir_name, _STATIC_DIR_NAME)
        for dir_name in (_IMG_DIR_NAME, _SCRIPTS_DIR_NAME, _STYLES_DIR_NAME):
            self._check_stop_operation()
            os.makedirs(os.path.join(self._static_dir_name, dir_name), exist_ok=True)

    def _draw_board(self) -> bool:
        """
        Method draws and saves an image of the board without pins.
        :return: True if the image was drawn and saved.
        """

        self._check_stop_operation()
        self.step_started.emit("Board drawing")
        logger.info("Board drawing...")

        if self._board.image:
            file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, _BOARD_IMAGE)
            ut.save_board(self._board.image, file_name)
            self.step_done.emit()
            logger.info("The board image is saved to '%s'", os.path.basename(file_name))
            return True

        self.step_done.emit()
        logger.info("The board image was not drawn")
        return False

    def _draw_board_with_pins(self, bad_pins: bool = False) -> bool:
        """
        Method draws and saves an image of the board with pins.
        :param bad_pins: if True, then the board will be drawn only with faulty pins.
        :return: True if the image was drawn and saved.
        """

        self._check_stop_operation()
        if bad_pins:
            pins_name = "faulty points"
            board_file_name = _BOARD_WITH_BAD_PINS_IMAGE
            pins = self._bad_pins_info
        else:
            pins_name = "points"
            board_file_name = _BOARD_WITH_PINS_IMAGE
            pins = self._pins_info
        self.step_started.emit(f"Board drawing with {pins_name}")
        logger.info("Board drawing with %s...", pins_name)

        self._check_stop_operation()
        if self._board.image:
            self._pin_diameter = ut.get_pin_diameter(self._board.image)
            file_name = os.path.join(self._static_dir_name, _IMG_DIR_NAME, board_file_name)
            ut.draw_board_with_pins(self._board.image, pins, file_name, self._pin_diameter, self._check_stop_operation)
            self.step_done.emit()
            logger.info("The board image with %s is saved to '%s'", pins_name, os.path.basename(file_name))
            return True

        self.step_done.emit()
        logger.info("The board image with %s was not drawn", pins_name)
        return False

    def _draw_fault_histogram(self) -> bool:
        """
        Method draws and saves a histogram of pin faults.
        :return: True if the histogram was drawn and saved.
        """

        self._check_stop_operation()
        self.step_started.emit("Fault histogram drawing")
        logger.info("Fault histogram drawing...")

        scores = [pin_info.score for pin_info in self._pins_info if pin_info.score is not None]
        if scores and self._threshold_score is not None:
            self._check_stop_operation()
            img_name = os.path.join(self._static_dir_name, _FAULT_HISTOGRAM_IMAGE)
            ut.draw_fault_histogram(scores, self._threshold_score, img_name, self._english)
            self.step_done.emit()
            logger.info("The fault histogram is saved to '%s'", img_name)
            return True

        self.step_done.emit()
        logger.info("The fault histogram was not drawn")
        return False

    def _draw_ivc(self) -> bool:
        """
        Method draws and saves IV-curves for the pins.
        :return: True if images were drawn and saved.
        """

        self._check_stop_operation()
        self.step_started.emit("IV-curves drawing")
        logger.info("IV-curves drawing...")
        if len(self._pins_info) > 0:
            img_dir_path = os.path.join(self._static_dir_name, _IMG_DIR_NAME)
            ut.draw_ivc_for_pins(self._pins_info, img_dir_path, self.step_done, self._scaling_type, self._english,
                                 self._user_defined_scales, self._check_stop_operation)
            logger.info("The IV-curve images are saved in the '%s' directory", img_dir_path)
            return True

        logger.info("There are no IV-curves to draw")
        return False

    def _generate_full_report(self) -> str:
        """
        Method generates a full report.
        :return: name of file with generated report.
        """

        self._check_stop_operation()
        self.step_started.emit("Generating a full report")
        logger.info("Generating a full report...")

        data = self._get_general_info()

        self._check_stop_operation()
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_FULL_REPORT)
        template_file_name = _TEMPLATE_FILE_WITH_FULL_REPORT_EN if self._english else _TEMPLATE_FILE_WITH_FULL_REPORT
        ut.generate_report(self._dir_template, template_file_name, report_file_name, **data)

        self.step_done.emit()
        logger.info("The full report is saved to '%s'", report_file_name)
        return report_file_name

    def _generate_report(self) -> str:
        """
        Method generates a short report. This report contains faulty pins.
        :return: name of file with generated report.
        """

        self._check_stop_operation()
        self.step_started.emit("Generating a report")
        logger.info("Generating a report...")

        data = self._get_general_info()
        data.update(self._get_info_about_faulty_elements_and_pins())

        self._check_stop_operation()
        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_REPORT)
        template_file_name = _TEMPLATE_FILE_WITH_REPORT_EN if self._english else _TEMPLATE_FILE_WITH_REPORT
        ut.generate_report(self._dir_template, template_file_name, report_file_name, **data)

        self.step_done.emit()
        self.generation_finished.emit(os.path.dirname(report_file_name))
        logger.info("The report is saved to '%s'", report_file_name)
        return report_file_name

    def _generate_report_with_map(self) -> Optional[str]:
        """
        Method generates a report with one big image of the board.
        :return: name of file with generated report.
        """

        if not self._results_by_steps[ReportCreationSteps.DRAW_BOARD]:
            self.step_done.emit()
            return

        self._check_stop_operation()
        self.step_started.emit("Generating a report with board map")
        logger.info("Generating a report with board map...")

        report_file_name = os.path.join(self._dir_name, _TEMPLATE_FILE_WITH_MAP)
        template_file_name = _TEMPLATE_FILE_WITH_MAP_EN if self._english else _TEMPLATE_FILE_WITH_MAP
        ut.generate_report(self._dir_template, template_file_name, report_file_name, pins=self._pins_info)

        self.step_done.emit()
        logger.info("The report with board map is saved to '%s'", report_file_name)
        return report_file_name

    def _get_faulty_pins(self) -> List[ut.PinInfo]:
        """
        :return: list with information about faulty pins. Faulty pins are pins whose score is greater or equal to
        the threshold.
        """

        self._check_stop_operation()
        faulty_pins = []
        if self._threshold_score is not None:
            faulty_pins = [pin_info for pin_info in self._pins_info
                           if pin_info.score is not None and pin_info.score >= self._threshold_score]
        return faulty_pins

    def _get_general_info(self) -> Dict[str, Any]:
        """
        :return: dictionary with general information.
        """

        self._check_stop_operation()
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

        self._check_stop_operation()
        return {"app_name": self._app_name,
                "app_version": self._app_version,
                "board_img_width": board_image_width,
                "computer": os.environ.get("COMPUTERNAME", "Unknown"),
                "date": datetime.strftime(datetime.now(), "%Y.%m.%d %H:%M:%S"),
                "elements_number": ut.get_elements_number(self._pins_info),
                "mm_per_px": mm_per_px,
                "operating_system": f"{platform.system()} {platform.release()} {platform.architecture()[0]}",
                "pcb_comment": pcb_comment,
                "pcb_name": pcb_name,
                "pin_img_size": pin_img_size,
                "pin_radius": _PIN_RADIUS if self._pin_diameter is None else int(self._pin_diameter / 2),
                "pins": self._pins_info,
                "pins_number": len(self._pins_info),
                "fault_histogram": self._results_by_steps[ReportCreationSteps.DRAW_FAULT_HISTOGRAM],
                "test_duration": self._test_duration,
                "threshold_score": self._threshold_score}

    def _get_info_about_faulty_elements_and_pins(self) -> Dict[str, Any]:
        """
        :return: dictionary with information about faulty elements and pins. Faulty pins are pins whose score is
        greater or equal to the threshold. Faulty element has at least one faulty pin.
        """

        self._check_stop_operation()
        return {"bad_elements_number": ut.get_elements_number(self._bad_pins_info),
                "bad_pins": self._bad_pins_info,
                "bad_pins_number": len(self._bad_pins_info)}

    def _get_pins(self) -> List[ut.PinInfo]:
        """
        :return: list with information about pins for which report should be generated.
        """

        comparator = IVCComparator()
        pins_info = []
        accounted_pin_index = 0
        total_pin_index = 0
        for element_index, element in enumerate(self._board.elements):
            for pin_index, pin in enumerate(element.pins):
                if (self._required_board or element_index in self._required_elements or
                        total_pin_index in self._required_pins):
                    if len(pin.measurements) > 1:
                        if isinstance(self._noise_amplitudes, (list, tuple)) and\
                                len(self._noise_amplitudes) > accounted_pin_index and\
                                len(self._noise_amplitudes[accounted_pin_index]) == 2:
                            voltage_noise, current_noise = self._noise_amplitudes[accounted_pin_index]
                        else:
                            voltage_noise, current_noise = ut.get_noise_amplitudes(pin)
                        comparator.set_min_ivc(voltage_noise, current_noise)
                        # Score is in relative units (0 - minimum value, 1 - maximum). Convert this value to %.
                        # The transition to percentages is carried out in the task # 85658
                        score = 100 * comparator.compare_ivc(pin.measurements[0].ivc, pin.measurements[1].ivc)
                    else:
                        score = None
                    pin_type = ut.get_pin_type(pin, score, self._threshold_score, self._is_report_for_test_board)
                    info = ut.PinInfo(element.name, element_index, pin_index, pin.x, pin.y, pin.measurements, score,
                                      pin_type, total_pin_index, pin.comment, pin.multiplexer_output)
                    pins_info.append(info)
                    accounted_pin_index += 1
                total_pin_index += 1
        pin_number = len(pins_info)
        self.total_number_of_steps_calculated.emit(self._get_total_number_of_steps(pin_number))
        return pins_info

    def _get_total_number_of_steps(self, pin_number: int) -> int:
        """
        :param pin_number: number of pins on the board.
        :return: total number of steps to generate all reports.
        """

        processes = (self._draw_board, self._draw_board_with_pins, self._draw_board_with_pins,
                     self._draw_fault_histogram, self._generate_report_with_map, self._generate_full_report,
                     self._generate_report)
        processes_for_pins = (self._draw_ivc,)
        return len(processes) + pin_number * len(processes_for_pins)

    def _read_config(self, config: Dict[ConfigAttributes, Any]) -> None:
        """
        Method reads dictionary with full information about required report.
        :param config: dictionary with full information about required report.
        """

        if not isinstance(config, dict):
            if not isinstance(self._config, dict):
                config = {ConfigAttributes.APP_NAME: None,
                          ConfigAttributes.APP_VERSION: None,
                          ConfigAttributes.BOARD: self._board,
                          ConfigAttributes.DIRECTORY: self._dir_name,
                          ConfigAttributes.ENGLISH: False,
                          ConfigAttributes.IS_REPORT_FOR_TEST_BOARD: None,
                          ConfigAttributes.NOISE_AMPLITUDES: None,
                          ConfigAttributes.OBJECTS: {},
                          ConfigAttributes.OPEN_REPORT_AT_FINISH: False,
                          ConfigAttributes.PIN_SIZE: _PIN_WIDTH,
                          ConfigAttributes.REPORTS_TO_OPEN: [ReportTypes.SHORT_REPORT],
                          ConfigAttributes.SCALING_TYPE: ut.ScalingTypes.AUTO,
                          ConfigAttributes.TEST_DURATION: None,
                          ConfigAttributes.THRESHOLD_SCORE: None,
                          ConfigAttributes.USER_DEFINED_SCALES: None}
            else:
                config = self._config
        self._config = config
        self._app_name = self._config.get(ConfigAttributes.APP_NAME, None)
        self._app_version = self._config.get(ConfigAttributes.APP_VERSION, None)
        self._board = self._config.get(ConfigAttributes.BOARD, self._board)
        parent_directory = self._config.get(ConfigAttributes.DIRECTORY, self._dir_name)
        self._dir_name = ut.create_report_directory_name(parent_directory, _DEFAULT_REPORT_DIR_NAME)
        self._english = self._config.get(ConfigAttributes.ENGLISH, False)
        self._is_report_for_test_board = self._config.get(ConfigAttributes.IS_REPORT_FOR_TEST_BOARD, None)
        self._noise_amplitudes = self._config.get(ConfigAttributes.NOISE_AMPLITUDES, None)
        self._open_report_at_finish = self._config.get(ConfigAttributes.OPEN_REPORT_AT_FINISH, False)
        self._pin_width = self._config.get(ConfigAttributes.PIN_SIZE, _PIN_WIDTH)
        self._reports_to_open = list(set(self._config.get(ConfigAttributes.REPORTS_TO_OPEN,
                                                          [ReportTypes.SHORT_REPORT])))
        self._scaling_type = self._config.get(ConfigAttributes.SCALING_TYPE, ut.ScalingTypes.AUTO)
        self._test_duration = self._config.get(ConfigAttributes.TEST_DURATION, None)
        self._test_duration = ut.get_duration_in_str(self._test_duration, self._english)
        threshold = self._config.get(ConfigAttributes.THRESHOLD_SCORE, None)
        if threshold is not None:
            # The threshold is given in relative units (0 - minimum value, 1 - maximum). Convert this value to %.
            # The transition to percentages is carried out in the task #85658
            self._threshold_score = 100 * threshold
        self._user_defined_scales = self._config.get(ConfigAttributes.USER_DEFINED_SCALES, None)
        required_objects = self._config.get(ConfigAttributes.OBJECTS, {})
        if required_objects.get(ObjectsForReport.BOARD):
            self._required_board = True
        else:
            self._required_board = False
            self._required_elements = required_objects.get(ObjectsForReport.ELEMENT, [])
            self._required_pins = required_objects.get(ObjectsForReport.PIN, [])

    def _run(self) -> None:
        """
        Method runs report generation.
        """

        if not isinstance(self._board, Board):
            return

        self._create_required_dirs()
        self._analyze_required_report_type()
        self._pins_info = self._get_pins()
        self._bad_pins_info = self._get_faulty_pins()
        if not self._pins_info:
            logger.info("There are no objects for which report should be created")
        methods = {ReportCreationSteps.DRAW_CLEAR_BOARD: self._draw_board,
                   ReportCreationSteps.DRAW_BOARD: (lambda: self._draw_board_with_pins(False)),
                   ReportCreationSteps.DRAW_BOARD_WITH_BAD_PINS: (lambda: self._draw_board_with_pins(True)),
                   ReportCreationSteps.DRAW_FAULT_HISTOGRAM: self._draw_fault_histogram,
                   ReportCreationSteps.DRAW_IV: self._draw_ivc}
        for step, method in methods.items():
            self._results_by_steps[step] = method()
        self._copy_favicon_and_styles()
        created_reports = {ReportTypes.MAP_REPORT: self._generate_report_with_map(),
                           ReportTypes.FULL_REPORT: self._generate_full_report(),
                           ReportTypes.SHORT_REPORT: self._generate_report()}
        if self._open_report_at_finish:
            for report_to_open in self._reports_to_open:
                report_file_name = created_reports.get(report_to_open, None)
                if report_file_name:
                    webbrowser.open(report_file_name, new=2)

    @classmethod
    def get_version(cls) -> str:
        """
        :return: version of package.
        """

        return VERSION

    def run(self, config: Dict[ConfigAttributes, Any]) -> None:
        """
        Method runs report generation.
        :param config: dictionary with full information about required report.
        """

        self._read_config(config)
        try:
            self._run()
            if self.stop:
                self.generation_stopped.emit()
        except UserStop:
            logger.info("Report generation stopped by user")
        except Exception as exc:
            error_str = f" ({exc})" if str(exc) else ""
            exception_text = f"An error occurred while generating the report{error_str}"
            self.exception_raised.emit(exception_text)
            logger.error(exception_text, exc_info=sys.exc_info())

    def stop_process(self) -> None:
        """
        Method stops report generation.
        """

        logger.info("User want to stop report generation")
        self.stop = True
