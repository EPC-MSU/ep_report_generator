"""
File with  useful functions.
"""

import copy
import logging
import os
from datetime import datetime, timedelta
from enum import auto, Enum
from typing import Callable, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from mako.template import Template
from PIL.Image import Image
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor, QFont
from epcore.elements import Board, Element, Pin
from ivviewer import Curve, Viewer

logger = logging.getLogger(__name__)


class PinTypes(Enum):
    """
    Types of pins.
    """

    HIGH_SCORE = 0
    LOW_SCORE = 1
    REFERENCE = 2


class ScalingTypes(Enum):
    """
    Scaling types for graph with IV-curves.
    """

    AUTO = auto()
    EYEPOINT_P10 = auto()
    USER_DEFINED = auto()


IV_IMAGE_SIZE = 300, 200
PIN_COLORS = {PinTypes.HIGH_SCORE: "#f00",
              PinTypes.LOW_SCORE: "#0f0",
              PinTypes.REFERENCE: "#f0f"}
REFERENCE_CURVE_COLOR = "#00f"
TEST_CURVE_COLOR = "#f00"


def _check_for_image_availability(func: Callable):
    """
    Decorator checks if there is image.
    :param func: decorated function.
    """

    def wrapper(image: Image, *args):
        if image is None:
            logger.warning("Board has no image")
            return False
        return func(image, *args)
    return wrapper


def _draw_circle(image: Image, circles: Tuple[List[float], List[float]], color: str) -> plt.Figure:
    """
    Function draws circle on image.
    :param image: image;
    :param circles: list of coordinates of circles to draw;
    :param color: color for circles.
    :return: figure.
    """

    dpi = plt.rcParams["figure.dpi"]
    height = image.height
    width = image.width
    fig_size = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.imshow(image, interpolation="nearest")
    marker_size = width // 35
    ax.scatter(*circles, s=marker_size, c=color, zorder=1)
    ax.set(xlim=[-0.5, width - 0.5], ylim=[height - 0.5, -0.5], aspect=1)
    return fig


def _get_pin_borders(center: float, board_width: int, pin_width: int) -> Tuple[float, float]:
    """
    Function defines boundaries of pin rectangle along one of axes.
    :param center: center of pin;
    :param board_width: width of board along axis;
    :param pin_width: width in pixels of pin image.
    :return: boundaries of pin rectangle.
    """

    left = center - pin_width // 2
    right = center + pin_width // 2
    if right > board_width:
        left -= right - board_width
        right = board_width
    if left < 0:
        right += -left
        left = 0
    return left, right


def calculate_distance(x_1: float, y_1: float, x_2: float, y_2: float) -> float:
    """
    Function calculates distance between two points.
    :param x_1: X coordinate of first point;
    :param y_1: Y coordinate of first point;
    :param x_2: X coordinate of second point;
    :param y_2: Y coordinate of second point.
    :return: distance between two points.
    """

    return np.sqrt(np.power(x_1 - x_2, 2) + np.power(y_1 - y_2, 2))


def calculate_min_distance(pins: list) -> Optional[float]:
    """
    Function calculates min distance between two pins.
    :param pins: list of pins.
    :return: min distance between two pins.
    """

    min_distance = None
    for pin in pins:
        pin_x = pin[3]
        pin_y = pin[4]
        for another_pin in pins:
            if pin == another_pin:
                continue
            another_pin_x = another_pin[3]
            another_pin_y = another_pin[4]
            distance = calculate_distance(pin_x, pin_y, another_pin_x, another_pin_y)
            if min_distance is None or min_distance > distance:
                min_distance = distance
    return min_distance


def create_board(test_board: Board, ref_board: Board) -> Board:
    """
    Function creates one board from test and reference boards.
    :param test_board: test board;
    :param ref_board: reference board.
    :return: board with test and reference IV-curves in pins.
    """

    board = Board()
    board.image = test_board.image
    board.pcb = test_board.pcb
    board.elements = []
    for element_index, element in enumerate(test_board.elements):
        board_pins = []
        for pin_index, pin in enumerate(element.pins):
            if pin.measurements:
                measurements = [copy.deepcopy(pin.measurements[0])]
                measurements[0].is_reference = False
            else:
                measurements = []
            if ref_board is not None:
                ref_measurements = ref_board.elements[element_index].pins[pin_index].measurements
                if ref_measurements:
                    measurements.append(copy.deepcopy(ref_measurements[0]))
                    measurements[-1].is_reference = True
            board_pins.append(Pin(x=pin.x, y=pin.y, measurements=measurements, comment=pin.comment,
                                  multiplexer_output=pin.multiplexer_output))
        board_element = Element(pins=board_pins, name=element.name, package=element.package,
                                bounding_zone=element.bounding_zone, rotation=element.rotation, width=element.width,
                                height=element.height, set_automatically=element.set_automatically)
        board.elements.append(board_element)
    return board


def create_report(template_file: str, report_file: str, **kwargs):
    """
    Function creates report.
    :param template_file: name of template file for report;
    :param report_file: name of file where report should be saved;
    :param kwargs: arguments for template.
    """

    report = Template(filename=template_file, input_encoding="utf-8")
    with open(report_file, "w", encoding="utf-8") as file:
        file.write(report.render(**kwargs))


def create_report_directory_name(parent_directory: str, dir_base: str) -> str:
    """
    Function creates name for directory where report will be saved.
    :param parent_directory: name of parent directory where directory with
    report will be placed;
    :param dir_base: base name for report directory.
    :return: path to report directory.
    """

    datetime_now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    report_dir_name_with_time = f"{dir_base} {datetime_now}"
    report_dir_name = report_dir_name_with_time
    index = 1
    while True:
        report_dir_path = os.path.join(parent_directory, report_dir_name)
        if os.path.exists(report_dir_path):
            index += 1
            report_dir_name = f"{report_dir_name_with_time} {index}"
        else:
            return report_dir_path


def create_test_and_ref_boards(board: Board) -> Tuple[Board, Board]:
    """
    Function creates two separate test and reference boards from one.
    :param board: initial board.
    :return: test and reference boards.
    """

    ref_elements = []
    test_elements = []
    for element in board.elements:
        ref_pins = []
        test_pins = []
        for pin in element.pins:
            ref_measurement = None
            test_measurement = None
            for measurement in pin.measurements:
                if measurement.is_reference:
                    ref_measurement = measurement
                else:
                    test_measurement = measurement
            ref_measurements = [] if ref_measurement is None else [ref_measurement]
            test_measurements = [] if test_measurement is None else [test_measurement]
            ref_pins.append(Pin(x=pin.x, y=pin.y, measurements=ref_measurements, comment=pin.comment,
                                multiplexer_output=pin.multiplexer_output))
            test_pins.append(Pin(x=pin.x, y=pin.y, measurements=test_measurements, comment=pin.comment,
                                 multiplexer_output=pin.multiplexer_output))
        ref_elements.append(Element(pins=ref_pins, name=element.name, package=element.package,
                                    bounding_zone=element.bounding_zone, rotation=element.rotation, width=element.width,
                                    height=element.height, set_automatically=element.set_automatically))
        test_elements.append(Element(pins=test_pins, name=element.name, package=element.package,
                                     bounding_zone=element.bounding_zone, rotation=element.rotation,
                                     width=element.width, height=element.height,
                                     set_automatically=element.set_automatically))
    ref_board = Board(elements=ref_elements, image=board.image, pcb=board.pcb)
    test_board = Board(elements=test_elements, image=board.image, pcb=board.pcb)
    return test_board, ref_board


@_check_for_image_availability
def draw_board_with_pins(image: Image, pins_info: List, file_name: str, marker_size: Optional[int]) -> bool:
    """
    Function draws and saves image of board with pins. Function was borrowed
    from https://stackoverflow.com/questions/34768717.
    :param image: board image;
    :param pins_info: list with information about pins required for report;
    :param file_name: name of file where image should be saved;
    :param marker_size: size of marker to display pin.
    :return: True if image was drawn and saved.
    """

    pins_xy = {PinTypes.HIGH_SCORE: [[], []],
               PinTypes.LOW_SCORE: [[], []],
               PinTypes.REFERENCE: [[], []]}
    for pin_info in pins_info:
        _, _, _, x, y, _, _, pin_type, _, _, _ = pin_info
        pin_xy = pins_xy[pin_type]
        pin_xy[0].append(x)
        pin_xy[1].append(y)
    dpi = plt.rcParams["figure.dpi"]
    height = image.height
    width = image.width
    fig_size = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.imshow(image, interpolation="nearest")
    if marker_size is None:
        marker_size = width // 38
    for pin_type, x_and_y in pins_xy.items():
        ax.scatter(*x_and_y, s=marker_size, c=PIN_COLORS[pin_type], zorder=1)
    fig.savefig(file_name, dpi=dpi, transparent=True)
    return True


def draw_ivc_for_pins(pins_info: List, dir_name: str, signal: pyqtSignal,
                      scaling_type: ScalingTypes = ScalingTypes.AUTO, english: bool = False,
                      stop_drawing: Callable = lambda: False, user_defined_scales: List = None):
    """
    Function draws and saves IV-curves for pins of board.
    :param pins_info: list with information about pins required for report;
    :param dir_name: name of directory where images should be saved;
    :param signal: signal;
    :param scaling_type: scaling type for graph with IV-curves;
    :param english: if True graph labels will be in English;
    :param stop_drawing: returns True if drawing should be stopped;
    :param user_defined_scales: list with user defined scales.
    """

    viewer = Viewer(axis_font=QFont("Times", 10), title_font=QFont("Times", 15))
    viewer.resize(*IV_IMAGE_SIZE)
    x_label = "Voltage, V" if english else "????????????????????, ??"
    viewer.plot.set_x_axis_title(x_label)
    y_label = "Current, mA" if english else "??????, ????"
    viewer.plot.set_y_axis_title(y_label)
    viewer.plot.setStyleSheet("background: white")
    test_curve = viewer.plot.add_curve()
    ref_curve = viewer.plot.add_curve()
    for index, pin_info in enumerate(pins_info):
        if stop_drawing():
            break
        element_name, element_index, pin_index, _, _, measurements, _, pin_type, _, _, _ = pin_info
        if not measurements:
            signal.emit()
            logger.info("Pin '%s_%s' has no measurements", element_index, pin_index)
            continue
        ref_currents = np.array([])
        ref_voltages = np.array([])
        test_currents = np.array([])
        test_voltages = np.array([])
        for measurement in measurements:
            if measurement.is_reference:
                ref_currents = measurement.ivc.currents
                ref_voltages = measurement.ivc.voltages
            else:
                test_currents = measurement.ivc.currents
                test_voltages = measurement.ivc.voltages
        if scaling_type == ScalingTypes.EYEPOINT_P10:
            v_max = np.ceil(measurements[0].settings.max_voltage)
            i_max = np.ceil(v_max * 1000 / measurements[0].settings.internal_resistance)
        elif (scaling_type == ScalingTypes.USER_DEFINED and isinstance(user_defined_scales, (list, tuple)) and
              index < len(user_defined_scales) and isinstance(user_defined_scales[index], (list, tuple)) and
              len(user_defined_scales[index]) == 2):
            v_max, i_max = user_defined_scales[index]
            i_max *= 1000
        else:
            i_max = 1.2 * 1000 * np.amax(np.absolute(np.concatenate((test_currents, ref_currents), axis=0)))
            v_max = 1.2 * np.amax(np.absolute(np.concatenate((test_voltages, ref_voltages), axis=0)))
        viewer.plot.set_scale(v_max, i_max)
        if ref_currents and ref_voltages:
            ref_curve.set_curve(Curve(ref_voltages, ref_currents))
            ref_curve.set_curve_params(QColor(REFERENCE_CURVE_COLOR))
        else:
            ref_curve.clear_curve()
        if test_currents and test_voltages:
            test_curve.set_curve(Curve(test_voltages, test_currents))
            test_curve.set_curve_params(QColor(TEST_CURVE_COLOR))
        else:
            test_curve.clear_curve()
        file_name = f"{element_index}_{pin_index}_iv.png"
        path = os.path.join(dir_name, file_name)
        viewer.plot.grab().save(path)
        signal.emit()
        logger.info("IV-curve of pin '%s_%s' was saved to '%s'", element_index, pin_index, file_name)


@_check_for_image_availability
def draw_pins(image: Image, pins_info: List, dir_name: str, signal: pyqtSignal, pin_width: int,
              stop_drawing: Callable = lambda: False) -> bool:
    """
    Function draws and saves images of pins of board.
    :param image: board image;
    :param pins_info: list with information about pins required for report;
    :param dir_name: name of directory where images should be saved;
    :param signal: signal;
    :param pin_width: width in pixels of pins images;
    :param stop_drawing: returns True if drawing should be stopped.
    :return: True if images were drawn and saved.
    """

    height = image.height
    width = image.width
    for pin_info in pins_info:
        if stop_drawing():
            return False
        element_name, element_index, pin_index, x, y, _, _, pin_type, _, _, _ = pin_info
        left, right = _get_pin_borders(x, width, pin_width)
        upper, lower = _get_pin_borders(y, height, pin_width)
        pin_image = image.crop((left, upper, right, lower))
        pin_color = PIN_COLORS[pin_type]
        fig = _draw_circle(pin_image, ([x - left], [y - upper]), pin_color)
        file_name = f"{element_index}_{pin_index}_pin.png"
        path = os.path.join(dir_name, file_name)
        fig.savefig(path)
        signal.emit()
        logger.info("Image of pin '%s_%s' was saved to '%s'", element_index, pin_index, file_name)
    return True


def draw_score_histogram(values: list, threshold: float, file_name: str):
    """
    Function draws and saves histogram of score values.
    :param values: score values to draw histogram;
    :param threshold: score threshold;
    :param file_name: name of file to save histogram.
    """

    fig = plt.figure(figsize=(6, 6))
    plt.hist(values, bins=80, range=([0, 1.0]))
    plt.axvline(x=threshold, color="red", linewidth=2)
    plt.yscale("symlog")
    plt.title("Score histogram")
    fig.savefig(file_name)
    fig.clear()


def get_duration_in_str(duration: timedelta, english: bool) -> Optional[str]:
    """
    Function returns duration in min and sec.
    :param duration: duration;
    :param english: if True then duration will be in English.
    :return: duration in min and sec.
    """

    duration_format = "{} min {} sec" if english else "{} ?????? {} ??????"
    if isinstance(duration, timedelta):
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return duration_format.format(minutes, seconds)
    return None


def get_pin_type(score: float, threshold_score: float) -> PinTypes:
    """
    Function determines type of pin.
    :param score: score of test measurement in pin;
    :param threshold_score: threshold score.
    :return: type of pin.
    """

    if threshold_score is not None and score is not None:
        pin_type = PinTypes.HIGH_SCORE if threshold_score <= score else PinTypes.LOW_SCORE
    else:
        pin_type = PinTypes.REFERENCE
    return pin_type
