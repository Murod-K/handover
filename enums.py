from enum import Enum


class Lang(str, Enum):
    RU = "ru"
    UZ = "uz"
    EN = "en"
    TR = "tr"


class ShiftType(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class NaturaStatus(str, Enum):
    GIVEN = "NATURA_GIVEN"
    NOT_GIVEN = "NATURA_NOT_GIVEN"
    WILL_BE_NIGHT = "NATURA_WILL_BE_NIGHT"


class RebarStatus(str, Enum):
    ACCEPTED = "REBAR_ACCEPTED"
    PARTIAL = "REBAR_PARTIAL"
    NOT_ACCEPTED = "REBAR_NOT_ACCEPTED"


class ConcretePlan(str, Enum):
    WILL_POUR = "WILL_POUR"
    NO_POUR = "NO_POUR"


class ReadinessStatus(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class UserRole(str, Enum):
    ADMIN = "admin"
    ENGINEER = "engineer"
