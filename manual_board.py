"""
File to create manual board.
"""

import numpy as np
from epcore.elements import Board, Element, IVCurve, Measurement, MeasurementSettings, PCBInfo, Pin


def create_manual_board(test: bool) -> Board:
    """
    Function creates board.
    :param test: if True then test board will be created otherwise reference board
    will be created.
    :return: board.
    """

    parameters_number = 4
    frequencies = 1, 100, 1000, 100000
    internal_resistances = 40, 400, 4000, 5000
    max_voltages = 1, 2, 3, 4
    errors = 5, 20, 40, 60
    elements_number = 3
    pins_number = 3
    elements = []
    index = 0
    for element_index in range(elements_number):
        element_name = f"Element_name_{element_index}"
        pins = []
        for pin_index in range(pins_number):
            x = element_index * 100 + pin_index * 2
            y = element_index * 100 + pin_index * 2
            comment_for_pin = f"This is comment for pin #{pin_index} of element {element_name}"
            settings = MeasurementSettings(sampling_rate=100 * frequencies[index],
                                           internal_resistance=internal_resistances[index],
                                           probe_signal_frequency=frequencies[index],
                                           max_voltage=max_voltages[index])
            error = errors[index] if test else 0
            iv_curve = get_iv_curve(index, error, settings)
            comment_for_measurement = (f"This is comment for measurement in pin #{pin_index} of "
                                       f"element {element_name}")
            is_dynamic = bool(index % 2)
            measurement = Measurement(settings=settings, ivc=iv_curve, comment=comment_for_measurement,
                                      is_dynamic=is_dynamic)
            pin = Pin(x=x, y=y, comment=comment_for_pin, measurements=[measurement])
            pins.append(pin)
            index = (index + 1) % parameters_number
        elements.append(Element(name=element_name, pins=pins))
    board = Board()
    board.pcb = PCBInfo(pcb_name="Manual board", comment="This board was made by hand for example")
    board.elements = elements
    return board


def get_circle(max_error: float) -> IVCurve:
    """
    Function returns IV-curve shaped as circle.
    :param max_error: max error for curve in percent.
    :return: circle-shaped curve.
    """

    points_number = 100
    errors = 1 + max_error * np.random.random(points_number) / 100
    t = np.linspace(0, 2 * np.pi, points_number)
    currents = list(np.cos(t) * errors / 1000)
    voltages = list(np.sin(t) * errors)
    return IVCurve(currents=currents, voltages=voltages)


def get_heart(max_error: float) -> IVCurve:
    """
    Function returns IV-curve shaped as heart.
    :param max_error: max error for curve in percent.
    :return: heart-shaped curve.
    """

    points_number = 100
    errors = 1 + max_error * np.random.random(points_number) / 100
    t = np.linspace(0, 2 * np.pi, points_number)
    currents = list((13 * np.cos(t) - 5 * np.cos(2 * t) - 2 * np.cos(3 * t) - np.cos(4 * t)) * errors / 1000)
    voltages = list(16 * np.power(np.sin(t), 3) * errors)
    return IVCurve(currents=currents, voltages=voltages)


def get_iv_curve(index: int, error: float, settings: MeasurementSettings) -> IVCurve:
    """
    Function returns IV-curve for different indices.
    :param index: index for curve;
    :param error: max error for curve in percent;
    :param settings: measurement settings.
    :return: IV-curve.
    """

    max_index = 4
    index = index % max_index
    if index == 0:
        curve = get_heart(error)
    elif index == 1:
        curve = get_shamrock(error)
    elif index == 2:
        curve = get_simple_curve(error)
    else:
        curve = get_circle(error)
    return scale_iv_curve(curve, settings)


def get_shamrock(max_error: float) -> IVCurve:
    """
    Function returns IV-curve shaped as shamrock.
    :param max_error: max error for curve in percent.
    :return: shamrock-shaped curve.
    """

    points_number = 100
    errors = 1 + max_error * np.random.random(points_number) / 100
    t = np.linspace(0, 2 * np.pi, points_number)
    currents = list(np.sin(3 * t) * np.sin(t) * errors / 1000)
    voltages = list(np.sin(3 * t) * np.cos(t) * errors)
    return IVCurve(currents=currents, voltages=voltages)


def get_simple_curve(max_error: float) -> IVCurve:
    """
    Function returns IV-curve.
    :param max_error: max error for curve in percent.
    :return: curve.
    """

    points_number = 100
    errors = 1 + max_error * np.random.random(points_number) / 100
    t = np.linspace(0, 2 * np.pi, points_number)
    currents = list(np.cos(3 * t) * errors / 1000)
    voltages = list(np.sin(t))
    return IVCurve(currents=currents, voltages=voltages)


def scale_iv_curve(curve: IVCurve, settings: MeasurementSettings) -> IVCurve:
    """
    Function returns rescaled IV-curve for given settings.
    :param curve: IV-curve to rescale;
    :param settings: measurement settings.
    :return: rescaled measurement settings.
    """

    currents = np.array(curve.currents)
    voltages = np.array(curve.voltages)
    max_current = np.amax(np.absolute(currents))
    max_voltage = np.amax(np.absolute(voltages))
    required_max_voltage = settings.max_voltage
    required_max_current = required_max_voltage / settings.internal_resistance
    currents = required_max_current / max_current * currents
    voltages = required_max_voltage / max_voltage * voltages
    return IVCurve(currents=list(currents), voltages=list(voltages))
