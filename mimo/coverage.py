
from typing import Optional


BITMAP_SIZE = 65536


def get_bitmap() -> bytearray:
    return bytearray(BITMAP_SIZE)


class BaseCoverage():
    """Basic result from the executor; subclasses include coverage constructs"""
    is_crash: bool
    # is_new is None until it is populated by the Scheduler
    is_new: Optional[bool]


class CoverageBitmap(BaseCoverage):
    """AFL-style bitmap"""
    def __init__(self):
        self.bitmap = get_bitmap()
        self.is_crash = False
        self.is_new: Optional[bool] = None
