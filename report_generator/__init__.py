"""
Package to generate report for Board object from epcore library.
"""

import logging
from report_generator.report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator, ReportTypes
from report_generator.utils import ScalingTypes
from report_generator.version import Version


__all__ = ["ConfigAttributes", "ObjectsForReport", "ReportGenerator", "ReportTypes", "ScalingTypes", "Version"]

mpl_logger = logging.getLogger("matplotlib")
mpl_logger.setLevel(logging.WARNING)
formatter = logging.Formatter("%(asctime)s %(name)s.%(funcName)s %(levelname)s - %(message)s",
                              datefmt="%Y-%m-%d %H:%M:%S")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
package_logger = logging.getLogger("report_generator")
package_logger.setLevel(logging.INFO)
package_logger.addHandler(handler)
package_logger.propagate = False
