from aiogram.types import InlineKeyboardButton

from src.domains.tracks.keyboards import get_retry_search_button


def test_get_retry_search_button():
    builder = get_retry_search_button("Повторить поиск")
    kb = builder.as_markup()
    assert any(isinstance(btn, InlineKeyboardButton) and btn.text == "Повторить поиск" for row in kb.inline_keyboard for btn in row)

