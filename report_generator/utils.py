"""
File with  useful functions.
"""

import json
import logging
import os
import time
from collections import namedtuple
from datetime import datetime, timedelta
from enum import auto, Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
import matplotlib.pyplot as plt
import numpy as np
from mako.lookup import TemplateLookup
from matplotlib.ticker import MaxNLocator, ScalarFormatter
from PIL.Image import Image
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QBrush, QColor, QFont, QPen
from epcore.elements import Pin
from ivviewer import Curve, Viewer


logger = logging.getLogger("report_generator")


PinInfo = namedtuple("PinInfo", ["element_name", "element_index", "pin_index", "x", "y", "measurements", "score",
                                 "pin_type", "total_pin_index", "comment", "multiplexer_output"])


class PinTypes(Enum):
    """
    Pin types.
    """

    REFERENCE_EMPTY = auto()
    REFERENCE_LOSS = auto()
    REFERENCE_NOT_EMPTY = auto()
    TEST_EMPTY = auto()
    TEST_HIGH_SCORE = auto()
    TEST_LOW_SCORE = auto()


class ScalingTypes(Enum):
    """
    Types of scaling of a graph with IV-curves.
    """

    AUTO = auto()
    EYEPOINT_P10 = auto()
    USER_DEFINED = auto()


IV_IMAGE_SIZE: Tuple[int, int] = (300, 200)
PIN_COLORS: Dict[PinTypes, str] = {PinTypes.REFERENCE_EMPTY: "#f0f",
                                   PinTypes.REFERENCE_LOSS: "#ff9900",
                                   PinTypes.REFERENCE_NOT_EMPTY: "#0f0",
                                   PinTypes.TEST_EMPTY: "#f0f",
                                   PinTypes.TEST_HIGH_SCORE: "#f00",
                                   PinTypes.TEST_LOW_SCORE: "#0f0"}
REFERENCE_CURVE_PEN: QPen = QPen(QBrush(QColor(0, 0, 255, 255)), 2)
TEST_CURVE_PEN: QPen = QPen(QBrush(QColor(255, 0, 0, 255)), 4)


def write_time(process_name: str):
    """
    A decorator that measures the execution time of the decorated operation and outputs it to the log.
    :param process_name: name of the operation whose execution time needs to be measured.
    """

    def decorator(func):
        """
        :param func: decorated function.
        """

        def wrapper(*args, **kwargs) -> Any:
            start_time = time.time()
            result = func(*args, **kwargs)
            logger.info("[TIME_SPENT] Time spent on the process '%s': %f sec", process_name, time.time() - start_time)
            return result

        return wrapper

    return decorator


@write_time("DRAW IVC FOR PIN")
def _draw_ivc_for_pin(pin_info: PinInfo, index: int, file_name: str, scaling_type: ScalingTypes,
                      user_defined_scales: list, viewer: Viewer, ref_curve, test_curve,
                      check_stop: Callable[[], None] = lambda: None) -> None:
    """
    :param pin_info: information about pin for which to draw IV-curve;
    :param index: pin index;
    :param file_name: name of the file in which to save the IV-curve image;
    :param scaling_type: type of scaling for a graph with IV-curve;
    :param user_defined_scales: list with user defined scales;
    :param viewer: widget in which to draw IV-curve;
    :param ref_curve: object into which to write data for the reference curve;
    :param test_curve: object into which to write data for the test curve;
    :param check_stop: function that checks whether the operation is stopped.
    """

    check_stop()
    ref_currents = np.array([])
    ref_voltages = np.array([])
    test_currents = np.array([])
    test_voltages = np.array([])
    for measurement in pin_info.measurements:
        if measurement.is_reference:
            ref_currents = measurement.ivc.currents
            ref_voltages = measurement.ivc.voltages
        else:
            test_currents = measurement.ivc.currents
            test_voltages = measurement.ivc.voltages

    check_stop()
    if scaling_type == ScalingTypes.EYEPOINT_P10:
        scale_coefficient = 1.2
        v_max = scale_coefficient * pin_info.measurements[0].settings.max_voltage
        i_max = 1000 * v_max / pin_info.measurements[0].settings.internal_resistance
    elif (scaling_type == ScalingTypes.USER_DEFINED and isinstance(user_defined_scales, (list, tuple)) and
          index < len(user_defined_scales) and isinstance(user_defined_scales[index], (list, tuple)) and
          len(user_defined_scales[index]) == 2):
        v_max, i_max = user_defined_scales[index]
        i_max *= 1000
    else:
        i_max = 1.2 * 1000 * np.amax(np.absolute(np.concatenate((test_currents, ref_currents), axis=0)))
        v_max = 1.2 * np.amax(np.absolute(np.concatenate((test_voltages, ref_voltages), axis=0)))
    viewer.plot.set_scale(v_max, i_max)

    check_stop()
    if len(ref_currents) and len(ref_voltages):
        ref_curve.set_curve(Curve(ref_voltages, ref_currents))
    else:
        ref_curve.clear_curve()
    if len(test_currents) and len(test_voltages):
        test_curve.set_curve(Curve(test_voltages, test_currents))
    else:
        test_curve.clear_curve()

    viewer.plot.grab().save(file_name, format="PNG")


def _get_pin_borders(center: float, board_width: int, pin_width: int) -> Tuple[float, float]:
    """
    Function defines the boundaries of the pin rectangle along one of the axes.
    :param center: pin center;
    :param board_width: board width along the axis;
    :param pin_width: width in pixels of the pin image.
    :return: boundaries of the pin rectangle.
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


def create_report_directory_name(parent_directory: str, dir_base: str) -> str:
    """
    Function creates name for directory where report will be saved.
    :param parent_directory: name of parent directory where directory with report will be placed;
    :param dir_base: base name for report directory.
    :return: path to report directory.
    """

    datetime_now = datetime.now().strftime("%Y-%m-%d %H-%M-%S")
    report_dir_name_with_time = f"{dir_base} {datetime_now}"
    report_dir_name = report_dir_name_with_time
    index = 0
    while True:
        report_dir_path = os.path.join(parent_directory, report_dir_name)
        if os.path.exists(report_dir_path):
            index += 1
            report_dir_name = f"{report_dir_name_with_time} {index}"
        else:
            return report_dir_path


@write_time("DRAW BOARD WITH PINS")
def draw_board_with_pins(image: Image, pins_info: list, file_name: str, marker_size: Optional[int],
                         check_stop: Callable[[], None] = lambda: None) -> None:
    """
    Function draws and saves an image of board with pins. Function was borrowed from
    https://stackoverflow.com/questions/34768717.
    :param image: board image;
    :param pins_info: list with information about pins to draw;
    :param file_name: name of file where image should be saved;
    :param marker_size: size of marker to display pin;
    :param check_stop: function that checks whether the operation is stopped.
    """

    pins_xy = {PinTypes.REFERENCE_EMPTY: [[], []],
               PinTypes.REFERENCE_LOSS: [[], []],
               PinTypes.REFERENCE_NOT_EMPTY: [[], []],
               PinTypes.TEST_EMPTY: [[], []],
               PinTypes.TEST_HIGH_SCORE: [[], []],
               PinTypes.TEST_LOW_SCORE: [[], []]}
    for pin_info in pins_info:
        check_stop()
        _, _, _, x, y, _, _, pin_type, _, _, _ = pin_info
        pin_xy = pins_xy[pin_type]
        pin_xy[0].append(x)
        pin_xy[1].append(y)

    check_stop()
    dpi = float(plt.rcParams["figure.dpi"])
    height = image.height
    width = image.width
    fig = plt.figure(figsize=(width / dpi, height / dpi))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.imshow(image, interpolation="nearest")

    if marker_size is None:
        marker_size = width // 38
    for pin_type, x_and_y in pins_xy.items():
        check_stop()
        ax.scatter(*x_and_y, s=marker_size, c=PIN_COLORS[pin_type], zorder=1)

    check_stop()
    fig.savefig(file_name, dpi=dpi, transparent=True)


@write_time("DRAW FAULT HISTOGRAM")
def draw_fault_histogram(scores: List[float], threshold: float, file_name: str, english: bool = False) -> None:
    """
    Function draws and saves a histogram of pin faults. The name of the histogram axes was chosen in the ticket #85658.
    :param scores: score values for which to draw a histogram;
    :param threshold: score threshold;
    :param file_name: name of file to save the histogram;
    :param english: if True histogram labels will be in English.
    """

    plt.rc("axes", labelsize=30)
    plt.rc("xtick", labelsize=20)
    plt.rc("ytick", labelsize=20)
    plt.rc("legend", fontsize=20)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    scores = np.array(scores)
    good_scores = [scores[index[0]] for index in np.argwhere(scores < threshold)]
    bins_number = 100
    y_values = np.array([])
    if good_scores:
        label = "Good points" if english else "Исправные\nточки"
        y_values, _, _ = ax.hist(good_scores, bins=bins_number, rwidth=0.85, color="#46CB18", alpha=0.7,
                                 range=([0, 100]), label=label)
    bad_scores = [scores[index[0]] for index in np.argwhere(scores >= threshold)]
    if bad_scores:
        label = "Faulty points" if english else "Неисправные\nточки"
        y_new, _, _ = ax.hist(bad_scores, bins=bins_number, rwidth=0.85, color="#E03C31", alpha=0.7, range=([0, 100]),
                              label=label)
        y_values = np.append(y_values, y_new)
    ax.axvline(x=threshold, color="#232B2B", linewidth=2, label="Threshold" if english else "Порог")
    ax.set_xlabel("Fault distribution" if english else "Распределение неисправностей")
    ax.set_xlim(xmin=0, xmax=100)
    ax.set_ylabel("Faults number" if english else "Количество неисправностей")
    ax.set_yscale("symlog")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    y_ticks_all = np.array([1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000])
    ax.set_yticks(y_ticks_all[y_ticks_all <= y_values.max()])
    plt.legend(loc="lower left", bbox_to_anchor=(0, 0.99, 1, 0.2), mode="expand", ncol=3)
    fig.savefig(file_name)
    fig.clear()


def draw_ivc_for_pins(pins_info: List[PinInfo], dir_name: str, signal: pyqtSignal,
                      scaling_type: ScalingTypes = ScalingTypes.AUTO, english: bool = False,
                      user_defined_scales: list = None, check_stop: Callable[[], None] = lambda: None) -> None:
    """
    Function draws and saves the IV-curves for the pins.
    :param pins_info: list with information about pins for which to draw IV-curves;
    :param dir_name: name of directory where images should be saved;
    :param signal: signal;
    :param scaling_type: type of scaling for a graph with IV-curve;
    :param english: if True, graph labels will be in English;
    :param user_defined_scales: list with user defined scales;
    :param check_stop: function that checks whether the operation is stopped.
    """

    check_stop()
    viewer = Viewer(axis_font=QFont("Times", 10), title_font=QFont("Times", 15))
    viewer.resize(*IV_IMAGE_SIZE)
    viewer.plot.set_min_borders(0.1, 0.1)
    viewer.plot.set_x_axis_title("Voltage, V" if english else "Напряжение, В")
    viewer.plot.set_y_axis_title("Current, mA" if english else "Ток, мА")
    viewer.plot.setStyleSheet("background: white")
    test_curve = viewer.plot.add_curve()
    test_curve.set_curve_params(TEST_CURVE_PEN)
    ref_curve = viewer.plot.add_curve()
    ref_curve.set_curve_params(REFERENCE_CURVE_PEN)

    for index, pin_info in enumerate(pins_info):
        check_stop()
        if not pin_info.measurements:
            signal.emit()
            logger.info("The pin '%s_%s' has no measurements", pin_info.element_index, pin_info.pin_index)
            continue

        file_name = os.path.join(dir_name, f"{pin_info.element_index}_{pin_info.pin_index}_iv.png")
        _draw_ivc_for_pin(pin_info, index, file_name, scaling_type, user_defined_scales, viewer, ref_curve, test_curve,
                          check_stop)
        signal.emit()
        logger.info("IV-curve of the pin '%s_%s' is saved to '%s'", pin_info.element_index, pin_info.pin_index,
                    os.path.basename(file_name))


@write_time("GENERATE REPORT")
def generate_report(template_dir: str, template_file: str, report_file: str, **kwargs) -> None:
    """
    Function generates a report.
    :param template_dir:
    :param template_file: name of template file for report;
    :param report_file: name of file where report should be saved;
    :param kwargs: arguments for template.
    """

    template_lookup = TemplateLookup(directories=[template_dir])
    template = template_lookup.get_template(template_file)
    with open(report_file, "w", encoding="utf-8") as file:
        kwargs["PIN_COLORS"] = json.dumps({str(key): value for key, value in PIN_COLORS.items()})
        file.write(template.render(**kwargs))


def get_default_dir_path() -> str:
    """
    :return: default path to the directory where report will be saved.
    """

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_duration_in_str(duration: timedelta, english: bool) -> Optional[str]:
    """
    Function returns duration in min and sec.
    :param duration: duration;
    :param english: if True then duration will be in English.
    :return: duration in min and sec.
    """

    duration_format = "{} min {} sec" if english else "{} мин {} сек"
    if isinstance(duration, timedelta):
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return duration_format.format(minutes, seconds)
    return None


def get_elements_number(pins_info: List[PinInfo]) -> int:
    """
    :param pins_info: list with information about pins.
    :return: number of different elements that pins from the list belong to.
    """

    return len({pin_info.element_index for pin_info in pins_info})


def get_noise_amplitudes(pin: Pin) -> Tuple[float, float]:
    """
    Function calculates noise amplitudes for given pin.
    :param pin: pin.
    :return: voltage and current noise amplitudes.
    """

    default_voltage_noise_amplitude = 0.6
    default_current_noise_amplitude = 0.2
    if pin.measurements:
        settings = pin.measurements[0].settings
        return settings.max_voltage / 20, 1000.0 * settings.max_voltage / (20 * settings.internal_resistance)
    return default_voltage_noise_amplitude, default_current_noise_amplitude


def get_pin_diameter(image: Image) -> Optional[int]:
    """
    :param image: image of the board with pins.
    :return: diameter of pins.
    """

    return image.width // 38 if image else None


def get_pin_type(pin: Pin, score: Optional[float], threshold_score: Optional[float], is_report_for_test_board: bool
                 ) -> PinTypes:
    """
    Function determines type of pin.
    :param pin: pin;
    :param score: score of test measurement in pin;
    :param threshold_score: threshold score;
    :param is_report_for_test_board: if True then report should be generated for test board, otherwise for reference
    board.
    :return: type of pin.
    """

    # Report for test board
    if is_report_for_test_board:
        if len(pin.measurements) < 2:
            return PinTypes.TEST_EMPTY
        if score is not None:
            if threshold_score is not None:
                return PinTypes.TEST_HIGH_SCORE if threshold_score <= score else PinTypes.TEST_LOW_SCORE
            return PinTypes.TEST_LOW_SCORE
        return PinTypes.TEST_LOW_SCORE

    # Report for reference board
    if len(pin.measurements) == 0:
        return PinTypes.REFERENCE_EMPTY
    if len(pin.measurements) == 1:
        if getattr(pin, "is_loss", None):
            return PinTypes.REFERENCE_LOSS
        return PinTypes.REFERENCE_NOT_EMPTY


@write_time("SAVE BOARD")
def save_board(image: Image, file_name: str) -> None:
    """
    :param image: board image to save;
    :param file_name: name of the file in which to save the board image.
    """

    image.save(file_name, "JPEG")
