import re
from datetime import datetime

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.common.message_pagination import show_msg_pagination
from src.domains.tracks.schemas import DownloadTrackParams
from src.domains.tracks.service import (
    TrackService,
)
from src.domains.tracks.track_name.keyboards import (
    kb_back_track_name_promt_item,
    kb_discipline,
    kb_show_final_result,
    kb_track_name_pagination,
)
from src.domains.tracks.track_name.message_cleanup import TrackNameMsgCleanerService
from src.domains.tracks.track_request.service import TrackRequestService
from src.domains.tracks.track_search.service import TrackSearchService
from src.domains.users.services import UserService
from src.service.downloader.service import DownloaderService

track_name_router = Router(name="track_name_router")


class TrackNameStates(StatesGroup):
    SECOND_NAME = State()
    FIRST_NAME = State()
    YEAR_OF_BIRTH = State()
    DISCIPLINE = State()
    CUSTOM_DISCIPLINE = State()


@track_name_router.callback_query(F.data == "set_track_name")
@inject
async def try_choose_track_name(
    callback: CallbackQuery,
    user_service: FromDishka[UserService],
    cleaner_service: FromDishka[TrackNameMsgCleanerService],
):
    await callback.answer()
    await _handle_search_tracks(
        callback=callback,
        user_service=user_service,
        cleaner_service=cleaner_service,
        page=1,
    )


@track_name_router.callback_query(F.data.startswith("track_name_page:"))
@inject
async def handle_search_tracks(
    callback: CallbackQuery,
    user_service: FromDishka[UserService],
    cleaner_service: FromDishka[TrackNameMsgCleanerService],
    page: int | None = None,
):
    if page is None:
        page = int(callback.data.split(":")[-1])
    await _handle_search_tracks(
        callback=callback,
        user_service=user_service,
        cleaner_service=cleaner_service,
        page=page,
    )


async def _handle_search_tracks(
    callback: CallbackQuery,
    user_service: UserService,
    cleaner_service: TrackNameMsgCleanerService,
    page: int | None = None,
):
    await callback.answer("Сейчас посмотрим, что вы вводили ранее...")

    user_track_names = await user_service.get_user_track_names(callback.from_user.id)
    keyboard = kb_track_name_pagination

    await show_msg_pagination(
        callback=callback,
        cleaner_service=cleaner_service,
        page=page,
        keyboard=keyboard,
        message_text="<b>Ранее вы вводили имена:</b>\n\n",
        data=user_track_names,
    )


@track_name_router.callback_query(F.data.startswith("t_p:"))
@inject
async def set_track_part(
    callback: CallbackQuery,
    state: FSMContext,
    cleaner_service: FromDishka[TrackNameMsgCleanerService],
) -> None:
    await callback.answer()

    data = callback.data.split("t_p:")[-1]

    second_name, first_name, year_of_birth = data.split("_")

    await state.update_data(first_name=first_name.upper())
    await state.update_data(second_name=second_name.capitalize())
    await state.update_data(year_of_birth=year_of_birth)
    await state.set_state(TrackNameStates.DISCIPLINE)
    send_msg = await show_discipline_interface(callback)
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=send_msg.message_id,
        user_id=callback.from_user.id,
    )


@track_name_router.callback_query(F.data == "hand_input_track_part")
async def set_second_name(callback: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(TrackNameStates.SECOND_NAME)
    await callback.message.edit_text(
        "Введите фамилию",
        reply_markup=kb_back_track_name_promt_item(callback_data="set_track_name"),
    )
    await callback.answer()


@track_name_router.message(TrackNameStates.SECOND_NAME)
async def set_first_name(message: Message, state: FSMContext) -> None:
    second_name = message.text.strip()
    if not second_name or not second_name.isalpha():
        await message.answer("Пожалуйста, введите фамилию только из букв.")
        return
    await state.update_data(second_name=second_name.capitalize())
    await state.set_state(TrackNameStates.FIRST_NAME)
    await message.answer(
        "Введите инициалы", reply_markup=kb_back_track_name_promt_item()
    )


@track_name_router.message(
    TrackNameStates.FIRST_NAME,
)
async def set_year_of_birth(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода инициалов.
    Сохраняет инициалы и переходит к следующему шагу — вводу года рождения.

    Аргументы:
        message (Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний.
    """
    first_name = message.text.strip()
    if not re.fullmatch(r"^[А-ЯЁ][А-ЯЁ]$", first_name):
        await message.answer("Пожалуйста, введите инициалы в формате: АА")
        return
    await state.update_data(first_name=first_name.upper())
    await state.set_state(TrackNameStates.YEAR_OF_BIRTH)
    await message.answer(
        "Введите год рождения", reply_markup=kb_back_track_name_promt_item()
    )


@track_name_router.message(TrackNameStates.YEAR_OF_BIRTH)
@inject
async def choose_discipline(
    message: Message, state: FSMContext, user_service: FromDishka[UserService]
) -> None:
    year_of_birth = message.text.strip()

    if not year_of_birth.isdigit():
        await message.answer("Пожалуйста, введите год рождения в формате: YYYY")
        return

    year = int(year_of_birth)
    current_year = datetime.now().year

    # Проверка: год в допустимом диапазоне
    if not (1970 <= year < current_year):
        await message.answer(f"Год рождения должен быть от 1970 до {current_year - 1}")
        return

    await state.update_data(year_of_birth=message.text)

    data_ = await state.get_data()
    await user_service.set_user_track_names(
        user_id=message.from_user.id,
        second_name=data_["second_name"],
        first_name=data_["first_name"],
        year_of_birth=data_["year_of_birth"],
    )

    await state.set_state(TrackNameStates.DISCIPLINE)
    await show_discipline_interface(message)


@track_name_router.callback_query(F.data.startswith("discipline:"))
@inject
async def process_discipline(
    callback: CallbackQuery,
    state: FSMContext,
    user_service: FromDishka[UserService],
    cleaner_service: FromDishka[TrackNameMsgCleanerService],
) -> None:
    value = callback.data.split(":", 1)[1]

    if value == "custom":
        await state.set_state(
            TrackNameStates.CUSTOM_DISCIPLINE,
        )
        send_msg = await callback.message.edit_text(
            """
            ✏️ Введи название дисциплины вручную:\n

Например: `«Акробатическая композиция»` или `«Свободное упражнение»`.
            """,
            reply_markup=kb_back_track_name_promt_item(callback_data="set_track_name"),
        )

        await cleaner_service.collect_cliper_messages_to_delete(
            message_id=send_msg.message_id,
            user_id=callback.from_user.id,
        )
    else:
        await state.update_data(discipline=value)
        send_msg = await show_final_result(
            message=callback.message,
            user_id=callback.from_user.id,
            state=state,
            user_service=user_service,
        )
        await cleaner_service.collect_cliper_messages_to_delete(
            message_id=send_msg.message_id,
            user_id=callback.from_user.id,
        )
        await callback.answer()


@track_name_router.message(TrackNameStates.CUSTOM_DISCIPLINE)
@inject
async def set_custom_discipline(
    message: Message,
    state: FSMContext,
    user_service: FromDishka[UserService],
    cleaner_service: FromDishka[TrackNameMsgCleanerService],
) -> None:
    await state.update_data(discipline=message.text)
    send_msg = await show_final_result(
        message=message,
        user_id=message.from_user.id,
        state=state,
        user_service=user_service,
    )
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=send_msg.message_id,
        user_id=message.from_user.id,
    )


# Обработчик "назад"
@track_name_router.callback_query(F.data == "go_back_track_name_item")
async def go_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == TrackNameStates.FIRST_NAME.state:
        await state.set_state(TrackNameStates.SECOND_NAME)
        await callback.message.edit_text(
            "Введите фамилию",
            reply_markup=kb_back_track_name_promt_item("set_track_name"),
        )
    elif current_state == TrackNameStates.YEAR_OF_BIRTH.state:
        await state.set_state(TrackNameStates.FIRST_NAME)
        await callback.message.edit_text(
            "Введите инициалы", reply_markup=kb_back_track_name_promt_item()
        )

    elif current_state == TrackNameStates.DISCIPLINE.state:
        await state.set_state(TrackNameStates.YEAR_OF_BIRTH)
        await callback.message.edit_text(
            "Введите год рождения", reply_markup=kb_back_track_name_promt_item()
        )

    elif current_state == TrackNameStates.CUSTOM_DISCIPLINE.state:
        await state.set_state(TrackNameStates.DISCIPLINE)
        await show_discipline_interface(callback)

    await callback.answer()


async def show_final_result(
    message: Message, user_id: int, state: FSMContext, user_service: UserService
) -> Message:
    track_name: str = await get_track_name(state)
    await user_service.set_session_track_names(user_id=user_id, track_name=track_name)
    send_msg = await message.answer(
        f"""
        📌 Ты выбрал название трека:\n

        <b>{track_name}</b>\n

        Всё верно?
        """,
        reply_markup=await kb_show_final_result(),
        parse_mode=ParseMode.HTML,
    )
    return send_msg


async def show_discipline_interface(event: CallbackQuery | Message) -> Message:
    message = event.message if isinstance(event, CallbackQuery) else event
    discipline_interface_msg = """
        🏅 Выбери дисциплину:\n\n
Можно выбрать из списка или ввести свою.
        """
    kb_dis = await kb_discipline()
    try:
        msg = await message.edit_text(
            discipline_interface_msg,
            reply_markup=kb_dis,
        )
    except TelegramBadRequest:
        msg = await message.answer(
            discipline_interface_msg,
            reply_markup=kb_dis,
        )
    return msg


@track_name_router.callback_query(F.data == "confirm_input")
@inject
async def confirm_input(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    downloader_service: FromDishka[DownloaderService],
    track_request_service: FromDishka[TrackRequestService],
    track_search_service: FromDishka[TrackSearchService],
    track_service: FromDishka[TrackService],
    user_service: FromDishka[UserService],
    cleaner_service: FromDishka[TrackNameMsgCleanerService],
):
    await cleaner_service.drop_clip_params_message(
        bot=bot, user_id=callback.from_user.id, chat_id=callback.from_user.id
    )

    state_data = await state.get_data()
    download_params = state_data.get("download_params")
    query_text = await user_service.get_session_query_text(callback.from_user.id)

    if not download_params:
        await track_search_service.search_tracks(
            callback=callback,
            bot=bot,
            state=state,
            downloader_service=downloader_service,
            track_request_service=track_request_service,
            query_text=query_text,
        )
    else:
        download_params = DownloadTrackParams(**download_params)
        await user_service.del_session_query_text(callback.from_user.id)
        track_path = await track_service.download_full_track(
            message=callback.message, download_params=download_params, bot=bot
        )
        await state.set_data({"track_path": track_path})


async def get_track_name(state: FSMContext) -> str:
    data = await state.get_data()
    return (
        f"{data['second_name']}_{data['first_name']}"
        f"_{data['year_of_birth']}_{data['discipline']}"
    )
