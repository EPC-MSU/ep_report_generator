from datetime import timedelta
import os
import unittest
from epcore.elements import Board, Element, IVCurve, Measurement, MeasurementSettings, Pin
from report_generator import utils as ut


class TestUtilsFunctions(unittest.TestCase):

    def test_calculate_distance_squared(self) -> None:
        self.assertEqual(ut.calculate_distance_squared(x_1=0, y_1=3, x_2=4, y_2=0), 5.0)

    def test_create_board(self) -> None:
        test_board = Board(elements=[
            Element(pins=[Pin(x=0, y=0,
                              measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                     internal_resistance=1,
                                                                                     max_voltage=1,
                                                                                     probe_signal_frequency=1),
                                                        ivc=IVCurve(currents=[0, 1, 2], voltages=[0, 1, 2]))])])])
        ref_board = Board(elements=[
            Element(pins=[Pin(x=0, y=0,
                              measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                     internal_resistance=1,
                                                                                     max_voltage=1,
                                                                                     probe_signal_frequency=1),
                                                        ivc=IVCurve(currents=[2, 1, 0], voltages=[2, 1, 0]))])])])
        result_board = Board(elements=[
            Element(pins=[Pin(x=0, y=0,
                              measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                     internal_resistance=1,
                                                                                     max_voltage=1,
                                                                                     probe_signal_frequency=1),
                                                        ivc=IVCurve(currents=[0, 1, 2], voltages=[0, 1, 2]),
                                                        is_reference=False),
                                            Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                     internal_resistance=1,
                                                                                     max_voltage=1,
                                                                                     probe_signal_frequency=1),
                                                        ivc=IVCurve(currents=[2, 1, 0], voltages=[2, 1, 0]),
                                                        is_reference=True)])])])
        board = ut.create_board(test_board, ref_board)
        self.assertEqual(board, result_board)

    def test_create_report_directory_name(self) -> None:
        dir_name = os.path.dirname(os.path.abspath(__file__))
        base_name = "BASE_NAME"
        report_dir_name = ut.create_report_directory_name(dir_name, base_name)
        self.assertFalse(os.path.exists(os.path.join(dir_name, report_dir_name)))
        self.assertTrue(report_dir_name.startswith(os.path.join(dir_name, base_name)))

    def test_get_duration_in_str(self) -> None:
        self.assertEqual(ut.get_duration_in_str(timedelta(hours=1, minutes=1, seconds=3), english=True),
                         "61 min 3 sec")
        self.assertEqual(ut.get_duration_in_str(timedelta(hours=2, minutes=31, seconds=43), english=False),
                         "151 мин 43 сек")

    def test_get_noise_amplitudes(self) -> None:
        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        self.assertEqual(ut.get_noise_amplitudes(pin), (1.0, 1.0))

        pin = Pin(x=0, y=0)
        self.assertEqual(ut.get_noise_amplitudes(pin), (0.6, 0.2))

    def test_get_pin_type(self) -> None:
        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        self.assertEqual(ut.get_pin_type(pin, None, None), ut.PinTypes.NOT_EMPTY)

        pin = Pin(x=0, y=0)
        self.assertEqual(ut.get_pin_type(pin, None, None), ut.PinTypes.EMPTY)

        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        pin.is_loss = True
        self.assertEqual(ut.get_pin_type(pin, None, None), ut.PinTypes.LOSS)

        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve()),
                                          Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        self.assertEqual(ut.get_pin_type(pin, 0.2, 0.6), ut.PinTypes.LOW_SCORE)
        self.assertEqual(ut.get_pin_type(pin, 0.2, 0.1), ut.PinTypes.HIGH_SCORE)
