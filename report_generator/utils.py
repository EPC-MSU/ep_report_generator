"""
File with  useful functions.
"""

import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, List, Optional, Tuple
from mako.lookup import TemplateLookup
from PIL.Image import Image
from epcore.elements import Measurement, Pin
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


def create_report_directory_base_name(project_name: Optional[str]) -> str:
    """
    :param project_name: the name of the project for which the report is generated.
    :return: folder name for project report.
    """

    if not project_name:
        return "report"

    project_name = project_name.replace(" ", "_")
    return f"{project_name}_report"


def create_report_directory_path(parent_directory: str, dir_base: str) -> str:
    """
    Function creates name for directory where report will be saved.
    :param parent_directory: name of parent directory where directory with report will be placed;
    :param dir_base: base name for report directory.
    :return: path to report directory.
    """

    datetime_now = datetime.now().strftime("%y-%m-%d_%H-%M")
    report_dir_name_with_time = f"{dir_base}_{datetime_now}"

    number = determine_number_of_directory(parent_directory, report_dir_name_with_time)
    if number == 1:
        report_dir_name = report_dir_name_with_time
    else:
        report_dir_name = f"{report_dir_name_with_time}_{number}"

    return os.path.join(parent_directory, report_dir_name)


def determine_number_of_directory(parent_directory: str, dir_base_name: str) -> int:
    """
    :param parent_directory: path to the parent directory;
    :param dir_base_name: base directory name.
    :return: number for a new directory that can be created in the parent directory. The new directory will be named
    'dir_base_name' if there are no directories with that base name, or 'dir_base_name_number' otherwise.
    """

    numbers = [0]
    if os.path.exists(parent_directory):
        for obj_name in os.listdir(parent_directory):
            path = os.path.join(parent_directory, obj_name)
            if os.path.isdir(path) and obj_name.startswith(dir_base_name):
                last_part = obj_name[len(dir_base_name):]
                result = re.match(r"^_(?P<number>\d+)$", last_part)
                if not last_part:
                    numbers.append(1)
                elif result:
                    numbers.append(int(result.group("number")))

    return max(numbers) + 1


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


def get_pin_type(pin: Optional[Pin], reference_measurement: Optional[Measurement],
                 test_measurement: Optional[Measurement], score: Optional[float], tolerance: Optional[float],
                 is_report_for_test_board: bool) -> PinTypes:
    """
    Function determines type of pin.
    :param pin: pin;
    :param reference_measurement: reference measurement;
    :param test_measurement: test measurement;
    :param score: difference of test measurement in pin;
    :param tolerance: tolerance;
    :param is_report_for_test_board: if True then report should be generated for test board, otherwise for reference
    board.
    :return: type of pin.
    """

    # Report for test board
    if is_report_for_test_board:
        if not test_measurement and not reference_measurement:
            return PinTypes.EMPTY

        if not test_measurement:
            return PinTypes.REFERENCE_ONLY

        if score is not None:
            return PinTypes.TEST_NONMATCHING if tolerance < score else PinTypes.TEST_MATCHING

        return PinTypes.TEST_MATCHING

    # Report for reference board
    if not reference_measurement:
        return PinTypes.EMPTY

    if getattr(pin, "is_loss", None):
        return PinTypes.REFERENCE_LOSS

    return PinTypes.REFERENCE_ONLY
