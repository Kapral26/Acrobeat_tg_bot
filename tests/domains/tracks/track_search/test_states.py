"""
Тесты для FSM-состояний поиска треков (FindTrackStates):
- Проверка корректности определения состояний.
"""

from aiogram.fsm.state import State

from src.domains.tracks.track_search.states import FindTrackStates


def test_find_track_states() -> None:
    """
    Проверяет, что состояния FSM корректно определены как экземпляры State.
    """
    assert isinstance(FindTrackStates.WAITING_FOR_PHRASE, State)
    assert isinstance(FindTrackStates.TRACK_NAME_CONFIRMED, State)
