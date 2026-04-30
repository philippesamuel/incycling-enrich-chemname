from enum import StrEnum


class ErrorFlags(StrEnum):
    ERROR = "ERROR"
    NOT_FOUND = "NOT_FOUND"


class ColEnum(StrEnum):
    NAME = "Name"
    CAS = "CAS-Number"
