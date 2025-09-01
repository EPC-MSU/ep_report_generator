from collections import namedtuple
from enum import auto, Enum
from typing import Dict


PinInfo = namedtuple("PinInfo", ["element_name", "element_index", "pin_index", "pin", "score", "pin_type",
                                 "total_pin_index"])


class PinTypes(Enum):
    """
    Pin types.
    """

    EMPTY = auto()
    REFERENCE_LOSS = auto()
    REFERENCE_ONLY = auto()
    TEST_MATCHING = auto()
    TEST_NONMATCHING = auto()


class ReportTypes(Enum):
    """
    Types of report.
    """

    FULL_REPORT = auto()
    MAP_REPORT = auto()
    SHORT_REPORT = auto()


class ScalingTypes(Enum):
    """
    Types of scaling of a graph with IV-curves.
    """

    AUTO = auto()
    EYEPOINT_P10 = auto()
    USER_DEFINED = auto()


PIN_COLORS: Dict[PinTypes, str] = {PinTypes.EMPTY: "#FF00FF",
                                   PinTypes.REFERENCE_LOSS: "#FFA500",
                                   PinTypes.REFERENCE_ONLY: "#0000FF",
                                   PinTypes.TEST_MATCHING: "#00FF00",
                                   PinTypes.TEST_NONMATCHING: "#FF0000"}
