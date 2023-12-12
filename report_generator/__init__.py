"""
Package to generate report for Board object from epcore library.
"""

from report_generator.logger import save_logs_to_file, set_logger, set_logging_level
from report_generator.reportgenerator import ConfigAttributes, ObjectsForReport, ReportGenerator
from report_generator.definitions import ReportTypes, ScalingTypes
from report_generator.version import VERSION


__all__ = ["ConfigAttributes", "ObjectsForReport", "ReportGenerator", "ReportTypes", "save_logs_to_file",
           "ScalingTypes", "set_logging_level", "VERSION"]
__version__ = VERSION
set_logger()
