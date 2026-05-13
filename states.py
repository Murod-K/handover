from aiogram.fsm.state import State, StatesGroup


class AuthStates(StatesGroup):
    waiting_code = State()
    choosing_lang = State()


class ShiftStates(StatesGroup):
    choosing_project = State()
    choosing_subproject = State()
    choosing_shift_type = State()
    # Entry loop
    choosing_structure_type = State()
    entering_structure_name = State()
    choosing_natura = State()
    choosing_rebar = State()
    choosing_defects = State()
    entering_custom_defect = State()
    choosing_concrete_plan = State()
    choosing_concrete_available = State()
    choosing_pour_method = State()
    choosing_pump_type = State()
    choosing_pump_logistics = State()
    entering_concrete_volume = State()
    choosing_formwork_ready = State()
    choosing_waterproof_ready = State()
    choosing_rebar_ready = State()
    entering_comment = State()
    # Confirmation
    entry_summary = State()


class AdminStates(StatesGroup):
    # Projects
    adding_project = State()
    adding_subproject_project = State()
    adding_subproject_name = State()
    # Structure types
    adding_structure_ru = State()
    adding_structure_icon = State()
    # Defect types
    adding_defect_ru = State()
    # Pour methods
    adding_pour_ru = State()
    adding_pour_pump_flag = State()
    # Pump types
    adding_pump_ru = State()
    # User management
    managing_users = State()
    # Invite codes
    gencode_count = State()
