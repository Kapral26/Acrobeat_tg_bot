from aiogram.fsm.state import StatesGroup, \
    State


class FindTrackStates(StatesGroup):
    WAITING_FOR_PHRASE = State()
    TRACK_NAME_CONFIRMED = State()
