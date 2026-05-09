from aiogram.fsm.state import State, StatesGroup


class LangSG(StatesGroup):
    choosing = State()


class MenuSG(StatesGroup):
    main = State()


class ShiftSG(StatesGroup):
    project    = State()
    subproject = State()
    shift_type = State()


class EntrySG(StatesGroup):
    structure_type  = State()
    structure_name  = State()
    natura          = State()
    rebar           = State()
    defects         = State()
    defect_custom   = State()
    concrete        = State()
    pour_method     = State()
    pump_type       = State()
    pump_logistics  = State()
    formwork        = State()
    waterproof      = State()
    rebar_for_pour  = State()
    volume          = State()
    comment         = State()
    entry_done      = State()


class AdminSG(StatesGroup):
    menu           = State()
    # Projects
    projects_list  = State()
    add_project    = State()
    project_detail = State()
    subprojects    = State()
    add_subproject = State()
    # Reference tables
    ref_list       = State()
    ref_add_ru     = State()
    ref_add_uz     = State()
    ref_add_en     = State()
    ref_add_tr     = State()
    ref_confirm_del = State()
