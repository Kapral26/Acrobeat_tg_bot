from src.domains.tracks.track_name.models import TrackNameRegistry


def test_track_name_registry_create():
    obj = TrackNameRegistry(id=1, user_id=2, track_part="TestPart")
    assert obj.id == 1
    assert obj.user_id == 2
    assert obj.track_part == "TestPart"


import pytest
from aiogram.types import InlineKeyboardButton

from src.domains.tracks.track_name.keyboards import kb_back_track_name_prompt_item, kb_show_final_result


def test_kb_back_track_name_prompt_item():
    kb = kb_back_track_name_prompt_item()
    assert any(
        isinstance(btn, InlineKeyboardButton)
        and btn.text == "\x1bb05\0 Назад"
        and btn.callback_data == "go_back_track_name_item"
        for row in kb.inline_keyboard
        for btn in row
    )


@pytest.mark.asyncio
async def test_kb_show_final_result():
    kb = await kb_show_final_result()
    texts = [btn.text for row in kb.inline_keyboard for btn in row]
    assert any("Изменить" in t for t in texts)
    assert any("Подтвердить" in t for t in texts)
