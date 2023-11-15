from collections import namedtuple
from enum import auto, Enum
from typing import Dict


PinInfo = namedtuple("PinInfo", ["element_name", "element_index", "pin_index", "x", "y", "measurements", "score",
                                 "pin_type", "total_pin_index", "comment", "multiplexer_output"])


class PinTypes(Enum):
    """
    Pin types.
    """

    REFERENCE_EMPTY = auto()
    REFERENCE_LOSS = auto()
    REFERENCE_NOT_EMPTY = auto()
    TEST_EMPTY = auto()
    TEST_HIGH_SCORE = auto()
    TEST_LOW_SCORE = auto()


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


PIN_COLORS: Dict[PinTypes, str] = {PinTypes.REFERENCE_EMPTY: "#f0f",
                                   PinTypes.REFERENCE_LOSS: "#ff9900",
                                   PinTypes.REFERENCE_NOT_EMPTY: "#0f0",
                                   PinTypes.TEST_EMPTY: "#f0f",
                                   PinTypes.TEST_HIGH_SCORE: "#f00",
                                   PinTypes.TEST_LOW_SCORE: "#0f0"}
