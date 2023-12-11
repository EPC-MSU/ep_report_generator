import logging
import os
from typing import Callable, List, Optional
import matplotlib
matplotlib.use("Agg")
# Trick to fix the flake8 error "E402 module level import not at top of file"
if True:
    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.ticker import MaxNLocator, ScalarFormatter
    from PIL.Image import Image
    from PyQt5.QtCore import pyqtSignal
    from PyQt5.QtGui import QBrush, QColor, QFont, QPen
    from ivviewer import Curve, Viewer
    from report_generator import utils as ut
    from report_generator.definitions import PIN_COLORS, PinInfo, PinTypes, ScalingTypes


logger = logging.getLogger("report_generator")


@ut.write_time("DRAW BOARD WITH PINS")
def draw_board_with_pins(image: Image, pins_info: List[PinInfo], file_name: str, marker_size: Optional[int],
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
        pin_xy = pins_xy[pin_info.pin_type]
        pin_xy[0].append(pin_info.x)
        pin_xy[1].append(pin_info.y)

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
    line_width = 1
    for pin_type, x_and_y in pins_xy.items():
        check_stop()
        ax.scatter(np.array(x_and_y[0]) - line_width, np.array(x_and_y[1]) - line_width, s=marker_size,
                   c=PIN_COLORS[pin_type], zorder=1, linewidths=line_width)

    check_stop()
    fig.savefig(file_name, dpi=dpi, transparent=True)


@ut.write_time("DRAW FAULT HISTOGRAM")
def draw_fault_histogram(scores: List[float], tolerance: float, file_name: str) -> None:
    """
    Function draws and saves a histogram of pin faults. The name of the histogram axes was chosen in the ticket #85658.
    :param scores: difference values for which to draw a histogram;
    :param tolerance: tolerance;
    :param file_name: name of file to save the histogram.
    """

    plt.rc("axes", labelsize=30)
    plt.rc("xtick", labelsize=20)
    plt.rc("ytick", labelsize=20)
    plt.rc("legend", fontsize=20)
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    scores = np.array(scores)
    good_scores = [scores[index[0]] for index in np.argwhere(scores < tolerance)]
    bins_number = 100
    if good_scores:
        ax.hist(good_scores, bins=bins_number, rwidth=0.85, color="#46CB18", alpha=0.7, range=([0, 100]),
                label=_("Исправные\nточки"))
    bad_scores = [scores[index[0]] for index in np.argwhere(scores >= tolerance)]
    if bad_scores:
        ax.hist(bad_scores, bins=bins_number, rwidth=0.85, color="#E03C31", alpha=0.7, range=([0, 100]),
                label=_("Неисправные\nточки"))
    ax.axvline(x=tolerance, color="#232B2B", linewidth=2, label=_("Допуск"))
    ax.set_xlabel(_("Распределение неисправностей"))
    ax.set_xlim(xmin=0, xmax=100)
    ax.set_ylabel(_("Количество неисправностей"))
    ax.set_yscale("symlog")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.yaxis.set_major_formatter(ScalarFormatter())
    plt.legend(loc="lower left", bbox_to_anchor=(0, 0.99, 1, 0.2), mode="expand", ncol=3)
    fig.savefig(file_name)
    fig.clear()


@ut.write_time("DRAW IVC FOR PIN")
def draw_ivc_for_pin(pin_info: PinInfo, index: int, file_name: str, scaling_type: ScalingTypes,
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


def draw_ivc_for_pins(pins_info: List[PinInfo], dir_name: str, signal: pyqtSignal,
                      scaling_type: ScalingTypes = ScalingTypes.AUTO, user_defined_scales: list = None,
                      check_stop: Callable[[], None] = lambda: None) -> None:
    """
    Function draws and saves the IV-curves for the pins.
    :param pins_info: list with information about pins for which to draw IV-curves;
    :param dir_name: name of directory where images should be saved;
    :param signal: signal;
    :param scaling_type: type of scaling for a graph with IV-curve;
    :param user_defined_scales: list with user defined scales;
    :param check_stop: function that checks whether the operation is stopped.
    """

    iv_image_size = 300, 200
    reference_curve_pen = QPen(QBrush(QColor(0, 0, 255, 255)), 2)
    test_curve_pen = QPen(QBrush(QColor(255, 0, 0, 255)), 4)

    check_stop()
    viewer = Viewer(axis_font=QFont("Times", 10), title_font=QFont("Times", 15))
    viewer.resize(*iv_image_size)
    viewer.plot.set_min_borders(0.1, 0.1)
    viewer.plot.set_x_axis_title(_("Напряжение, В"))
    viewer.plot.set_y_axis_title(_("Ток, мА"))
    viewer.plot.setStyleSheet("background: white")
    test_curve = viewer.plot.add_curve(_("Тестовая ВАХ"))
    test_curve.set_curve_params(test_curve_pen)
    ref_curve = viewer.plot.add_curve(_("ВАХ эталона"))
    ref_curve.set_curve_params(reference_curve_pen)
    viewer.plot.show_legend(QFont("Times", 10))

    for index, pin_info in enumerate(pins_info):
        check_stop()
        if not pin_info.measurements:
            signal.emit()
            logger.info("The pin '%s_%s' has no measurements", pin_info.element_index, pin_info.pin_index)
            continue

        file_name = os.path.join(dir_name, f"{pin_info.element_index}_{pin_info.pin_index}_iv.png")
        draw_ivc_for_pin(pin_info, index, file_name, scaling_type, user_defined_scales, viewer, ref_curve, test_curve,
                         check_stop)
        signal.emit()
        logger.info("IV-curve of the pin '%s_%s' is saved to '%s'", pin_info.element_index, pin_info.pin_index,
                    os.path.basename(file_name))


@ut.write_time("SAVE BOARD")
def save_board(image: Image, file_name: str) -> None:
    """
    :param image: board image to save;
    :param file_name: name of the file in which to save the board image.
    """

    if image.mode in ("RGBA", "P"):
        image_to_save = image.convert("RGB")
    else:
        image_to_save = image
    image_to_save.save(file_name, "JPEG")
