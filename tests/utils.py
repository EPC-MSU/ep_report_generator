import numpy as np
from epcore.elements import Board, Element, IVCurve, Measurement, MeasurementSettings, Pin


def create_simple_board(test: bool) -> Board:
    """
    Function creates simple board.
    :param test: if True then test board will be created otherwise reference board will be created.
    :return: board.
    """

    frequency = 100000
    internal_resistance = 40
    max_voltage = 1.0
    elements_number = 1
    pins_number = 2
    elements = []
    for element_index in range(elements_number):
        pins = []
        for pin_index in range(pins_number):
            settings = MeasurementSettings(sampling_rate=100 * frequency,
                                           internal_resistance=internal_resistance,
                                           probe_signal_frequency=frequency,
                                           max_voltage=max_voltage)
            current_max = 1000 * max_voltage / internal_resistance / 2
            voltage_max = max_voltage / 2
            iv_curve = IVCurve(currents=list(np.linspace(-current_max, current_max, 100)),
                               voltages=list(np.linspace(-voltage_max, voltage_max, 100)))
            pin = Pin(x=0, y=0, measurements=[Measurement(settings=settings, ivc=iv_curve, is_reference=not test)])
            pins.append(pin)
        elements.append(Element(name=f"Element_name_{element_index}", pins=pins))
    board = Board()
    board.elements = elements
    return board
