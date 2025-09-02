"""
Модуль `handlers.py` содержит обработчики событий для взаимодействия с историей поисковых запросов пользователей.

Обрабатывает:
- открытие истории запросов;
- пагинацию списка запросов;
- выбор конкретного запроса из истории.
"""

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.common.message_pagination import show_msg_pagination
from src.domains.tracks.track_request.keyboards import (
    kb_confirm_track_request,
    kb_no_track_request,
    kb_user_track_request,
)
from src.domains.tracks.track_request.service import TrackRequestService
from src.domains.users.services import UserService

track_request_router = Router(name="track_request_router")


@track_request_router.callback_query(F.data == "set_track_request")
@inject
async def try_choose_track_name(
    callback: CallbackQuery,
    track_request_service: FromDishka[TrackRequestService],
) -> None:
    """
    Обработчик для открытия истории поисковых запросов пользователя.

    Запускает отображение первой страницы истории запросов.

    :param callback: CallbackQuery от нажатия кнопки "Моя история".
    :param track_request_service: Сервис для работы с запросами на поиск треков.
    """
    await callback.answer()
    await _handle_request_tracks(callback, track_request_service, page=1)


@track_request_router.callback_query(F.data.startswith("track_request_page:"))
@inject
async def handle_request_tracks(
    callback: CallbackQuery,
    track_request_service: FromDishka[TrackRequestService],
    page: int | None = None,
) -> None:
    """
    Обработчик для навигации по страницам истории запросов.

    Извлекает данные о запросах пользователя и отображает их с пагинацией.

    :param callback: CallbackQuery с данными о номере страницы.
    :param track_request_service: Сервис для работы с запросами на поиск треков.
    :param page: Номер текущей страницы (определяется из callback.data).
    """
    if page is None:
        page = int(callback.data.split(":")[-1])
    await _handle_request_tracks(callback, track_request_service, page)


async def _handle_request_tracks(
    callback: CallbackQuery,
    track_request_service: TrackRequestService,
    page: int | None = None,
) -> None:
    """
    Вспомогательная функция для отображения истории запросов пользователя.

    Получает список запросов, формирует клавиатуру с пагинацией и отправляет сообщение с результатами.

    :param callback: CallbackQuery от пользователя.
    :param track_request_service: Сервис для работы с запросами на поиск треков.
    :param page: Номер страницы для отображения.
    """
    await callback.answer("Сейчас посмотрим, что вы искали ранее...")

    user_track_requests = await track_request_service.get_track_user_request(
        callback.from_user.id
    )

    if not user_track_requests:
        await callback.message.edit_text(
            """📂 История пуста.\n\n
Ты ещё не искал треки.\n
Начни новый поиск 👇""",
            reply_markup=await kb_no_track_request(),
        )
        return

    keyboard = kb_user_track_request

    await show_msg_pagination(
        callback=callback,
        page=page,
        keyboard=keyboard,
        message_text="<b>📂 Твои прошлые запросы:</b>\n\nВыбери один из них или задай новый 🎵",
        data=user_track_requests,
    )


@track_request_router.callback_query(F.data.startswith("t_r:"))
@inject
async def callback_query(
    callback: CallbackQuery,
    _state: FSMContext,
    user_service: FromDishka[UserService],
) -> None:
    """
    Обработчик для выбора конкретного запроса из истории.

    Сохраняет выбранный текст запроса в сессию пользователя и запрашивает подтверждение.

    :param callback: CallbackQuery с данными о выбранном запросе.
    :param _state: Состояние FSM для управления диалогом.
    :param user_service: Сервис для работы с пользователями.
    """
    await callback.answer()
    query_text = callback.data.split(":")[-1]
    await user_service.set_session_query_text(callback.from_user.id, query_text)

    await callback.message.edit_text(
        f"📌 Ты выбрал: <b>{query_text}</b>\n\nПодтвердить выбор?",
        reply_markup=await kb_confirm_track_request(),
        parse_mode="html",
    )
