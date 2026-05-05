from enum import Enum


class Language(str, Enum):
    RU = "ru"
    UZ = "uz"
    EN = "en"
    TR = "tr"


class ShiftType(str, Enum):
    DAY = "DAY"
    NIGHT = "NIGHT"


class StructureType(str, Enum):
    COLUMN = "COLUMN"
    WALL = "WALL"
    SLAB = "SLAB"
    BEAM = "BEAM"
    FOUNDATION = "FOUNDATION"


class NaturaStatus(str, Enum):
    GIVEN = "NATURA_GIVEN"
    NOT_GIVEN = "NATURA_NOT_GIVEN"
    WILL_BE_NIGHT = "NATURA_WILL_BE_NIGHT"


class RebarStatus(str, Enum):
    ACCEPTED = "REBAR_ACCEPTED"
    PARTIAL = "REBAR_PARTIAL"
    NOT_ACCEPTED = "REBAR_NOT_ACCEPTED"


class RebarDefect(str, Enum):
    NO_COVER = "DEFECT_NO_COVER"
    MISSING_TIES = "DEFECT_MISSING_TIES"
    MISSING_BOLTS = "DEFECT_MISSING_BOLTS"
    WRONG_SPACING = "DEFECT_WRONG_SPACING"
    FRAME_SHIFT = "DEFECT_FRAME_SHIFT"
    BINDING_INCOMPLETE = "DEFECT_BINDING_INCOMPLETE"
    GEODESY_NOT_READY = "DEFECT_GEODESY_NOT_READY"
    NO_CLEANING = "DEFECT_NO_CLEANING"
    CUSTOM = "DEFECT_CUSTOM"


class ConcretePlan(str, Enum):
    WILL_POUR = "CONCRETE_WILL_POUR"
    NO_POUR = "CONCRETE_NO_POUR"


class ConcreteAvailable(str, Enum):
    YES = "CONCRETE_AVAILABLE"
    NO = "CONCRETE_NOT_AVAILABLE"


class ReadinessStatus(str, Enum):
    READY = "READY"
    NOT_READY = "NOT_READY"


class PourMethod(str, Enum):
    STATIONARY_PUMP = "POURING_STATIONARY_PUMP"
    MOBILE_PUMP = "POURING_MOBILE_PUMP"
    MANUAL = "POURING_MANUAL"
    NOT_APPLICABLE = "POURING_NOT_APPLICABLE"


class PumpType(str, Enum):
    SPIDER_32_4 = "PUMP_SPIDER_32_4"
    PUMP_20_4 = "PUMP_20_4"
    OTHER = "PUMP_OTHER"


class PumpLogistics(str, Enum):
    ASSEMBLY = "LOGISTICS_ASSEMBLY"
    RELOCATION = "LOGISTICS_RELOCATION"
    BOTH = "LOGISTICS_BOTH"
    NONE = "LOGISTICS_NONE"
