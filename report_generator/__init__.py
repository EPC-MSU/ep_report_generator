"""
Package to generate report for Board object from epcore library.
"""

import logging
from .report_generator import ConfigAttributes, ObjectsForReport, ReportGenerator, RequirementTypes
from .version import Version

__all__ = ["ConfigAttributes", "ObjectsForReport", "ReportGenerator", "RequirementTypes", "Version"]

formatter = logging.Formatter("%(asctime)s - %(name)s - %(message)s")
handler = logging.StreamHandler()
handler.setFormatter(formatter)
handler.setLevel(logging.INFO)
package_logger = logging.getLogger(__name__.split('.')[0])
package_logger.setLevel(logging.INFO)
package_logger.addHandler(handler)
package_logger.propagate = False
