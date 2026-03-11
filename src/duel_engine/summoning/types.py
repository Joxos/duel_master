from __future__ import annotations

from enum import Enum


class SummonType(str, Enum):
    NORMAL = "NORMAL"
    FLIP = "FLIP"
    SET = "SET"


class ExtraSummonType(str, Enum):
    FUSION = "FUSION"
    SYNCHRO = "SYNCHRO"
    XYZ = "XYZ"


class LinkSummonType(str, Enum):
    LINK = "LINK"
