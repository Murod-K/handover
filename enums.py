from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    SENIOR = "senior"
    ENGINEER = "engineer"


class ShiftType(str, Enum):
    DAY = "day"
    NIGHT = "night"


class NaturaStatus(str, Enum):
    GIVEN = "NATURA_GIVEN"
    NOT_GIVEN = "NATURA_NOT_GIVEN"
    WILL_BE_NIGHT = "NATURA_WILL_BE_NIGHT"


class RebarStatus(str, Enum):
    DONE = "REBAR_DONE"
    PARTIAL = "REBAR_PARTIAL"
    NOT_DONE = "REBAR_NOT_DONE"


class ConcretePlan(str, Enum):
    YES = "CONCRETE_YES"
    NO = "CONCRETE_NO"


class PumpLogistics(str, Enum):
    MOUNT = "PUMP_MOUNT"
    MOVE = "PUMP_MOVE"
    BOTH = "PUMP_BOTH"
    NONE = "PUMP_NONE"
