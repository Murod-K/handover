from aiogram.fsm.state import State, StatesGroup


class LanguageStates(StatesGroup):
    choosing = State()


class ProjectStates(StatesGroup):
    choosing_project = State()
    choosing_subproject = State()


class ShiftStates(StatesGroup):
    choosing_shift_type = State()
    confirming = State()


class EntryStates(StatesGroup):
    # Structure
    choosing_structure_type = State()
    entering_structure_name = State()

    # Natura (разрешение на работу)
    choosing_natura = State()

    # Rebar
    choosing_rebar_status = State()
    choosing_rebar_defects = State()
    entering_rebar_comment = State()

    # Concrete
    choosing_concrete_plan = State()
    checking_concrete_available = State()
    choosing_formwork_ready = State()
    choosing_waterproof_ready = State()
    choosing_rebar_ready_for_pour = State()
    entering_concrete_volume = State()
    choosing_pour_method = State()
    choosing_pump_type = State()
    choosing_pump_logistics = State()
    entering_pump_logistics_detail = State()

    # Entry comment
    entering_entry_comment = State()

    # After entry done
    entry_done = State()
