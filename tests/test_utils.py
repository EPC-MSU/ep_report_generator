import os
import unittest
from datetime import timedelta
from collections import namedtuple
from epcore.elements import IVCurve, Measurement, MeasurementSettings, Pin
from report_generator import utils as ut


class TestUtilsFunctions(unittest.TestCase):

    def test_create_report_directory_name(self) -> None:
        dir_name = os.path.dirname(os.path.abspath(__file__))
        base_name = "BASE_NAME"
        report_dir_name = ut.create_report_directory_name(dir_name, base_name)
        self.assertFalse(os.path.exists(os.path.join(dir_name, report_dir_name)))
        self.assertTrue(report_dir_name.startswith(os.path.join(dir_name, base_name)))

    def test_get_duration_in_str(self) -> None:
        self.assertEqual(ut.get_duration_in_str(timedelta(hours=1, minutes=1, seconds=3)), "61 мин 3 сек")
        self.assertEqual(ut.get_duration_in_str(timedelta(hours=2, minutes=31, seconds=43)), "151 мин 43 сек")

    def test_get_elements_number(self) -> None:
        pins = [ut.PinInfo("name_1", 1, 1, 0, 0, [], 0, None, 0, None, None),
                ut.PinInfo("name_1", 2, 1, 0, 0, [], 0, None, 0, None, None),
                ut.PinInfo("name_1", 3, 1, 0, 0, [], 0, None, 0, None, None),
                ut.PinInfo("name_1", 1, 1, 0, 0, [], 0, None, 0, None, None),
                ut.PinInfo("name_1", 2, 1, 0, 0, [], 0, None, 0, None, None)]
        self.assertEqual(ut.get_elements_number(pins), 3)

    def test_get_noise_amplitudes(self) -> None:
        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        self.assertEqual(ut.get_noise_amplitudes(pin), (1.0, 1.0))

        pin = Pin(x=0, y=0)
        self.assertEqual(ut.get_noise_amplitudes(pin), (0.6, 0.2))

    def test_get_pin_diameter(self) -> None:
        self.assertIsNone(ut.get_pin_diameter(None))

        Image = namedtuple("Image", ["width"])
        image = Image(76)
        self.assertEqual(ut.get_pin_diameter(image), 2)

    def test_get_pin_type(self) -> None:
        pin = Pin(x=0, y=0)
        self.assertEqual(ut.get_pin_type(pin, None, None, False), ut.PinTypes.REFERENCE_EMPTY)

        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        pin.is_loss = True
        self.assertEqual(ut.get_pin_type(pin, None, None, False), ut.PinTypes.REFERENCE_LOSS)

        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        self.assertEqual(ut.get_pin_type(pin, None, None, False), ut.PinTypes.REFERENCE_NOT_EMPTY)

        pin = Pin(x=0, y=0, measurements=[Measurement(settings=MeasurementSettings(sampling_rate=1,
                                                                                   internal_resistance=1000.0,
                                                                                   max_voltage=20.0,
                                                                                   probe_signal_frequency=1),
                                                      ivc=IVCurve())])
        self.assertEqual(ut.get_pin_type(pin, None, None, True), ut.PinTypes.TEST_EMPTY)

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
        self.assertEqual(ut.get_pin_type(pin, 0.2, 0.6, True), ut.PinTypes.TEST_LOW_SCORE)
        self.assertEqual(ut.get_pin_type(pin, 0.2, 0.1, True), ut.PinTypes.TEST_HIGH_SCORE)
