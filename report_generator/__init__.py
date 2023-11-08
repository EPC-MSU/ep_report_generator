"""
Package to generate report for Board object from epcore library.
"""

from report_generator.logger import set_logger
from report_generator.reportgenerator import ConfigAttributes, ObjectsForReport, ReportGenerator, ReportTypes
from report_generator.utils import ScalingTypes
from report_generator.version import VERSION


__all__ = ["ConfigAttributes", "ObjectsForReport", "ReportGenerator", "ReportTypes", "ScalingTypes", "VERSION"]
__version__ = VERSION
set_logger()
