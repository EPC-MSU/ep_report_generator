"""
File with  useful functions.
"""

import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple
from mako.lookup import TemplateLookup
from PIL.Image import Image
from epcore.elements import Pin
from report_generator.definitions import PIN_COLORS, PinInfo, PinTypes


logger = logging.getLogger("report_generator")


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


def convert_dict_to_json(data: dict):
    """
    :param data: dictionary to be converted to JSON.
    :return: serialized dictionary.
    """

    return json.dumps({str(key): value for key, value in data.items()})


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


@write_time("GENERATE REPORT")
def generate_report(template_dir: str, template_file: str, report_file: str, **kwargs) -> None:
    """
    Function generates a report.
    :param template_dir: directory where the report template is located;
    :param template_file: name of template file for report;
    :param report_file: name of file where report should be saved;
    :param kwargs: arguments for template.
    """

    template_lookup = TemplateLookup(directories=[template_dir])
    template = template_lookup.get_template(template_file)
    with open(report_file, "w", encoding="utf-8") as file:
        kwargs["PIN_COLORS"] = convert_dict_to_json(PIN_COLORS)
        file.write(template.render(**kwargs))


def get_default_dir_path() -> str:
    """
    :return: default path to the directory where report will be saved.
    """

    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_duration_in_str(duration: timedelta) -> Optional[str]:
    """
    Function returns duration in min and sec.
    :param duration: duration.
    :return: duration in min and sec.
    """

    if isinstance(duration, timedelta):
        minutes = int(duration.total_seconds() // 60)
        seconds = int(duration.total_seconds() % 60)
        return _("{} мин {} сек").format(minutes, seconds)
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


def get_pin_type(pin: Pin, score: Optional[float], tolerance: Optional[float], is_report_for_test_board: bool
                 ) -> PinTypes:
    """
    Function determines type of pin.
    :param pin: pin;
    :param score: difference of test measurement in pin;
    :param tolerance: tolerance;
    :param is_report_for_test_board: if True then report should be generated for test board, otherwise for reference
    board.
    :return: type of pin.
    """

    # Report for test board
    if is_report_for_test_board:
        if len(pin.measurements) < 2:
            return PinTypes.TEST_EMPTY
        if score is not None:
            if tolerance is not None:
                return PinTypes.TEST_HIGH_SCORE if tolerance < score else PinTypes.TEST_LOW_SCORE
            return PinTypes.TEST_LOW_SCORE
        return PinTypes.TEST_LOW_SCORE

    # Report for reference board
    if len(pin.measurements) == 0:
        return PinTypes.REFERENCE_EMPTY
    if len(pin.measurements) == 1:
        if getattr(pin, "is_loss", None):
            return PinTypes.REFERENCE_LOSS
        return PinTypes.REFERENCE_NOT_EMPTY
