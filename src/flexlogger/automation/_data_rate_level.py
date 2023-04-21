from enum import Enum


class DataRateLevel(Enum):
    """An enumeration describing the possible data rate levels that channels can be configured to use.
    For additional information on configuring data rates, visit
    https://www.ni.com/docs/en-US/bundle/flexlogger/page/configuring-data-rates.html
    """

    SLOW = 1
    """The slow analog data rate level in Hertz at which your DAQ device acquires data."""

    MEDIUM = 2
    """The medium analog data rate level in Hertz at which your DAQ device acquires data."""

    FAST = 3
    """The fast analog data rate level in Hertz at which your DAQ device acquires data."""

    COUNTER = 4
    """The counter data rate level in Hertz at which your DAQ device acquires data."""

    DIGITAL = 6
    """The digital data rate level in Hertz at which your DAQ device acquires data."""

    ON_DEMAND = 7
    """The on-demand data rate level in Hertz at which your DAQ device acquires data."""
