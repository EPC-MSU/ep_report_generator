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


def _get_pin_type(pin: "Pin") -> PinTypes:
    """
    Function determines type of pin.
    :param pin: pin.
    :return: type of pin.
    """

    pin_type = PinTypes.EMPTY
    if len(pin.measurements):
        if pin.measurements[0].is_dynamic:
            pin_type = PinTypes.DYNAMIC
        elif pin.measurements[0].is_reference:
            pin_type = PinTypes.REFERENCE
        else:
            pin_type = PinTypes.NORMAL
    return pin_type


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


def draw_board_with_pins(board: Board, file_name: str):
    """
    Function draws and saves image of board with pins. Function was borrowed
    from https://stackoverflow.com/questions/34768717.
    :param board: board;
    :param file_name: name of file where image should be saved.
    """

    pins_xy = {PinTypes.DYNAMIC: [[], []],
               PinTypes.EMPTY: [[], []],
               PinTypes.HIGH_SCORE: [[], []],
               PinTypes.NORMAL: [[], []],
               PinTypes.REFERENCE: [[], []]}
    for element in board.elements:
        for pin in element.pins:
            pin_type = _get_pin_type(pin)
            pin_xy = pins_xy[pin_type]
            pin_xy[0].append(pin.x)
            pin_xy[1].append(pin.y)
    dpi = plt.rcParams["figure.dpi"]
    height = board.image.height
    width = board.image.width
    fig_size = width / float(dpi), height / float(dpi)
    fig = plt.figure(figsize=fig_size)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.axis("off")
    ax.imshow(board.image, interpolation="nearest")
    marker_size = width // 35
    for pin_type, x_and_y in pins_xy.items():
        ax.scatter(*x_and_y, s=marker_size, c=PIN_COLORS[pin_type], zorder=1)
    ax.set(xlim=[-0.5, width - 0.5], ylim=[height - 0.5, -0.5], aspect=1)
    fig.savefig(file_name, dpi=dpi, transparent=True)


def draw_ivc_for_pins(board: Board, dir_name: str):
    """
    Function draws and saves IV-curves for pins of board.
    :param board: board;
    :param dir_name: name of directory where images should be saved.
    """

    viewer = Viewer()
    viewer.resize(*IV_IMAGE_SIZE)
    curve = viewer.plot.add_curve()
    for element_index, element in enumerate(board.elements):
        for pin_index, pin in enumerate(element.pins):
            pin_type = _get_pin_type(pin)
            if pin_type is not PinTypes.EMPTY:
                currents = pin.measurements[0].ivc.currents
                voltages = pin.measurements[0].ivc.voltages
                i_max = 1.2 * 1000 * np.amax(np.absolute(currents))
                v_max = 1.2 * np.amax(np.absolute(voltages))
                viewer.plot.set_scale(v_max, i_max)
                curve.set_curve(Curve(voltages, currents))
                curve.set_curve_params(QColor(PIN_COLORS[pin_type]))
            else:
                curve.clear_curve()
            file_name = f"{element.name}_{element_index}_{pin_index}_iv.png"
            path = os.path.join(dir_name, file_name)
            viewer.plot.grab().save(path)
            logger.info("IV-curve of pin '%s_%s_%s' was saved to '%s'", element.name, element_index,
                        pin_index, file_name)


def draw_pins(board: Board, dir_name: str):
    """
    Function draws and saves images of pins of board.
    :param board: board;
    :param dir_name: name of directory where images should be saved.
    """

    height = board.image.height
    width = board.image.width
    for element_index, element in enumerate(board.elements):
        for pin_index, pin in enumerate(element.pins):
            pin_type = _get_pin_type(pin)
            left, right = _get_pin_borders(pin.x, width)
            upper, lower = _get_pin_borders(pin.y, height)
            pin_image = board.image.crop((left, upper, right, lower))
            pin_color = PIN_COLORS[pin_type]
            fig = _draw_circle(pin_image, ([pin.x - left], [pin.y - upper]), pin_color)
            file_name = f"{element.name}_{element_index}_{pin_index}_pin.png"
            path = os.path.join(dir_name, file_name)
            fig.savefig(path)
            logger.info("Image of pin '%s_%s_%s' was saved to '%s'", element.name, element_index,
                        pin_index, file_name)
