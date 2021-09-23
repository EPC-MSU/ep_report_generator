"""
File with  useful functions.
"""

import logging
from enum import Enum
import matplotlib.pyplot as plt
from epcore.elements import Board

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


PIN_COLORS = {PinTypes.DYNAMIC: "magenta",
              PinTypes.EMPTY: "purple",
              PinTypes.HIGH_SCORE: "red",
              PinTypes.NORMAL: "blue",
              PinTypes.REFERENCE: "orange"}


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
            pin_type = PinTypes.EMPTY
            if len(pin.measurements):
                if pin.measurements[0].is_dynamic:
                    pin_type = PinTypes.DYNAMIC
                elif pin.measurements[0].is_reference:
                    pin_type = PinTypes.REFERENCE
                else:
                    pin_type = PinTypes.NORMAL
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
