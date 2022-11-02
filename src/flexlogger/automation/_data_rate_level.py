from enum import Enum


class DataRateLevel(Enum):
    """An enumeration describing the possible data rate levels."""

    SLOW = 1
    MEDIUM = 2
    FAST = 3
    COUNTER = 4
    DIGITAL = 6
    ON_DEMAND = 7
