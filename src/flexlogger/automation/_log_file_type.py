from enum import Enum

class LogFileType(Enum):
    """An enumeration describing the different log file types."""

    TDMS = 0
    """TDMS files"""

    TDMS_BACKUP_FILES = 1
    """TDMS backup files"""

    CSV = 2
    """CSV files"""