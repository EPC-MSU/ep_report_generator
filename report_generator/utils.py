"""
File with  useful functions.
"""

import logging
import os
from enum import Enum
from typing import List, Tuple
import matplotlib.pyplot as plt
import numpy as np
from mako.template import Template
from PIL.Image import Image
from PyQt5.QtGui import QColor
from epcore.elements import Board
from ivviewer import Curve, Viewer

logger = logging.getLogger(__name__)


class PinTypes(Enum):
    """
    Types of pins.
    """

    DYNAMIC = 0
    EMPTY = 1
    HIGH_SCORE = 2
    NORMAL = 3
    REFERENCE = 4


IV_IMAGE_SIZE = 300, 200
PIN_COLORS = {PinTypes.DYNAMIC: "magenta",
              PinTypes.EMPTY: "purple",
              PinTypes.HIGH_SCORE: "red",
              PinTypes.NORMAL: "blue",
              PinTypes.REFERENCE: "orange"}
PIN_HALF_WIDTH = 50


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


def _get_pin_borders(center: float, board_width: int) -> Tuple[float, float]:
    """
    Function defines boundaries of pin rectangle along one of axes.
    :param center: center of pin;
    :param board_width: width of board along axis.
    :return: boundaries of pin rectangle.
    """

    left = center - PIN_HALF_WIDTH
    right = center + PIN_HALF_WIDTH
    if right > board_width:
        left -= right - board_width
        right = board_width
    if left < 0:
        right += -left
        left = 0
    return left, right


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
    for element_index, element in enumerate(test_board.elements):
        for pin_index, pin in enumerate(element.pins):
            measurements = pin.measurements
            if measurements:
                measurements[0].is_reference = False
                measurements = [measurements[0]]
            else:
                measurements = []
            if ref_board is not None:
                ref_measurements = ref_board.elements[element_index].pins[pin_index].measurements
                if ref_measurements:
                    ref_measurements[0].is_reference = True
                    measurements.append(ref_measurements[0])
            pin.measurements = measurements
    board.elements = test_board.elements
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


def draw_board_with_pins(image: Image, pins_info: List, file_name: str):
    """
    Function draws and saves image of board with pins. Function was borrowed
    from https://stackoverflow.com/questions/34768717.
    :param image: board image;
    :param pins_info: list with information about pins required for report;
    :param file_name: name of file where image should be saved.
    """

    pins_xy = {PinTypes.DYNAMIC: [[], []],
               PinTypes.EMPTY: [[], []],
               PinTypes.HIGH_SCORE: [[], []],
               PinTypes.NORMAL: [[], []],
               PinTypes.REFERENCE: [[], []]}
    for pin_info in pins_info:
        _, _, _, x, y, _, _, pin_type, _ = pin_info
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
    marker_size = width // 35
    for pin_type, x_and_y in pins_xy.items():
        ax.scatter(*x_and_y, s=marker_size, c=PIN_COLORS[pin_type], zorder=1)
    ax.set(xlim=[-0.5, width - 0.5], ylim=[height - 0.5, -0.5], aspect=1)
    fig.savefig(file_name, dpi=dpi, transparent=True)


def draw_ivc_for_pins(pins_info: List, dir_name: str):
    """
    Function draws and saves IV-curves for pins of board.
    :param pins_info: list with information about pins required for report;
    :param dir_name: name of directory where images should be saved.
    """

    viewer = Viewer()
    viewer.resize(*IV_IMAGE_SIZE)
    test_curve = viewer.plot.add_curve()
    ref_curve = viewer.plot.add_curve()
    for pin_info in pins_info:
        element_name, element_index, pin_index, _, _, measurements, _, pin_type, _ = pin_info
        if pin_type is not PinTypes.EMPTY:
            test_currents = measurements[0].ivc.currents
            test_voltages = measurements[0].ivc.voltages
            if len(measurements) > 1:
                ref_currents = measurements[1].ivc.currents
                ref_voltages = measurements[1].ivc.voltages
            else:
                ref_currents = np.array([])
                ref_voltages = np.array([])
            i_max = 1.2 * 1000 * np.amax(np.absolute(np.concatenate((test_currents, ref_currents),
                                                                    axis=0)))
            v_max = 1.2 * np.amax(np.absolute(np.concatenate((test_voltages, ref_voltages),
                                                             axis=0)))
            viewer.plot.set_scale(v_max, i_max)
            test_curve.set_curve(Curve(test_voltages, test_currents))
            test_curve.set_curve_params(QColor(PIN_COLORS[pin_type]))
            if len(measurements) > 1:
                ref_curve.set_curve(Curve(ref_voltages, ref_currents))
                ref_curve.set_curve_params(QColor(PIN_COLORS[PinTypes.REFERENCE]))
            else:
                ref_curve.clear_curve()
        else:
            test_curve.clear_curve()
            ref_curve.clear_curve()
        file_name = f"{element_name}_{element_index}_{pin_index}_iv.png"
        path = os.path.join(dir_name, file_name)
        viewer.plot.grab().save(path)
        logger.info("IV-curve of pin '%s_%s_%s' was saved to '%s'", element_name, element_index,
                    pin_index, file_name)


def draw_pins(image: Image, pins_info: List, dir_name: str):
    """
    Function draws and saves images of pins of board.
    :param image: board image;
    :param pins_info: list with information about pins required for report;
    :param dir_name: name of directory where images should be saved.
    """

    height = image.height
    width = image.width
    for pin_info in pins_info:
        element_name, element_index, pin_index, x, y, _, _, pin_type, _ = pin_info
        left, right = _get_pin_borders(x, width)
        upper, lower = _get_pin_borders(y, height)
        pin_image = image.crop((left, upper, right, lower))
        pin_color = PIN_COLORS[pin_type]
        fig = _draw_circle(pin_image, ([x - left], [y - upper]), pin_color)
        file_name = f"{element_name}_{element_index}_{pin_index}_pin.png"
        path = os.path.join(dir_name, file_name)
        fig.savefig(path)
        logger.info("Image of pin '%s_%s_%s' was saved to '%s'", element_name, element_index,
                    pin_index, file_name)


def get_pin_type(measurements: List["Measurement"], score: float, threshold_score: float) ->\
        PinTypes:
    """
    Function determines type of pin.
    :param measurements: list of measurements in pin;
    :param score: score of test measurement in pin;
    :param threshold_score: threshold score.
    :return: type of pin.
    """

    pin_type = PinTypes.EMPTY
    if len(measurements):
        if threshold_score is not None and score is not None and threshold_score <= score:
            pin_type = PinTypes.HIGH_SCORE
        elif measurements[0].is_reference:
            pin_type = PinTypes.REFERENCE
        elif measurements[0].is_dynamic:
            pin_type = PinTypes.DYNAMIC
        else:
            pin_type = PinTypes.NORMAL
    return pin_type
