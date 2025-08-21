import re
from datetime import datetime

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.handlers import search_tracks
from src.domains.tracks.track_name.keyboards import (
    back_track_name_button,
    discipline_keyboard,
    edit_track_name_keyboard,
    user_track_name_parts_keyboard,
)
from src.domains.users.services import UserService

track_name_router = Router(name="track_name_router")


class TrackNameStates(StatesGroup):
    """
    Класс состояний для FSM-машинки, связанной с вводом данных трека.

    Атрибуты:
        SECOND_NAME: Состояние для ввода фамилии.
        FIRST_NAME: Состояние для ввода инициалов.
        YEAR_OF_BIRTH: Состояние для ввода года рождения.
    """

    SECOND_NAME = State()
    FIRST_NAME = State()
    YEAR_OF_BIRTH = State()
    DISCIPLINE = State()
    CUSTOM_DISCIPLINE = State()


@track_name_router.callback_query(F.data == "set_track_name")
@inject
async def try_choose_track_name(
    callback: CallbackQuery, user_service: FromDishka[UserService]
):
    await callback.answer()
    await _handle_search_tracks(callback, user_service, page=1)


ITEM_PER_PAGE = 4


@track_name_router.callback_query(F.data.startswith("track_name_page:"))
@inject
async def handle_search_tracks(
    callback: CallbackQuery,
    user_service: FromDishka[UserService],
    page: int | None = None,
):
    if page is None:
        page = int(callback.data.split(":")[-1])
    await _handle_search_tracks(callback, user_service, page)


async def _handle_search_tracks(
    callback: CallbackQuery,
    user_service: UserService,
    page: int | None = None,
):
    await callback.answer("Сейчас посмотрим, что вы вводили ранее...")

    user_track_parts = await user_service.get_user_track_names(callback.from_user.id)

    total_pages = (len(user_track_parts) + ITEM_PER_PAGE - 1) // ITEM_PER_PAGE
    start_idx = (page - 1) * ITEM_PER_PAGE
    end_idx = start_idx + ITEM_PER_PAGE

    current_page = user_track_parts[start_idx:end_idx]
    message_text = "<b>Ранее введенные данные:</b>\n\n"
    await callback.message.edit_text(
        message_text,
        parse_mode="html",
        reply_markup=await user_track_name_parts_keyboard(
            current_page, page, total_pages
        ),
    )


@track_name_router.callback_query(F.data.startswith("t_p:"))
async def set_track_part(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()

    data = callback.data.split("t_p:")[-1]

    second_name, first_name, year_of_birth = data.split("_")

    await state.update_data(first_name=first_name.upper())
    await state.update_data(second_name=second_name.capitalize())
    await state.update_data(year_of_birth=year_of_birth)
    await state.set_state(TrackNameStates.DISCIPLINE)
    await callback.message.answer(
        "Выберите спортивную дисциплину", reply_markup=discipline_keyboard()
    )


@track_name_router.callback_query(F.data == "hand_input_track_part")
async def set_second_name(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик нажатия кнопки "Установить имя трека".
    Устанавливает состояние ввода фамилии и запрашивает у пользователя ввод.

    Аргументы:
        callback (CallbackQuery): Объект callback-запроса от пользователя.
        state (FSMContext): Контекст машины состояний.
    """
    await state.set_state(TrackNameStates.SECOND_NAME)
    await callback.message.edit_text(
        "Введите фамилию", reply_markup=back_track_name_button()
    )
    await callback.answer()


@track_name_router.message(TrackNameStates.SECOND_NAME)
async def set_first_name(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода фамилии.
    Сохраняет фамилию и переходит к следующему шагу — вводу инициалов.

    Аргументы:
        message (Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний.
    """
    second_name = message.text.strip()
    if not second_name or not second_name.isalpha():
        await message.answer("Пожалуйста, введите фамилию только из букв.")
        return
    await state.update_data(second_name=second_name.capitalize())
    await state.set_state(TrackNameStates.FIRST_NAME)
    await message.answer("Введите инициалы", reply_markup=back_track_name_button())


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
    await message.answer("Введите год рождения", reply_markup=back_track_name_button())


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

    await user_service.set_user_track_names(
        user_id=message.from_user.id, **(await state.get_data())
    )

    await state.set_state(TrackNameStates.DISCIPLINE)
    await message.answer(
        "Выберите спортивную дисциплину", reply_markup=discipline_keyboard()
    )


@track_name_router.callback_query(F.data.startswith("discipline:"))
async def process_discipline(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]

    if value == "custom":
        await state.set_state(
            TrackNameStates.CUSTOM_DISCIPLINE,
        )
        await callback.message.edit_text(
            "Введите дисциплину вручную", reply_markup=back_track_name_button()
        )
    else:
        await state.update_data(discipline=value)
        await show_final_result(callback.message, state)
        await callback.answer()


@track_name_router.message(
    TrackNameStates.CUSTOM_DISCIPLINE,
    lambda message: message.text and message.text.isalpha(),
)
async def set_custom_discipline(message: Message, state: FSMContext) -> None:
    custom_discipline = message.text.strip()
    if not custom_discipline or not custom_discipline.isalpha():
        await message.answer("Пожалуйста, введите дисциплину только из букв.")
        return
    await state.update_data(discipline=message.text)
    await show_final_result(message, state)


# Обработчик "назад"
@track_name_router.callback_query(F.data == "go_back_track_name_item")
async def go_back(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == TrackNameStates.FIRST_NAME.state:
        await state.set_state(TrackNameStates.SECOND_NAME)
        await callback.message.edit_text(
            "Введите фамилию", reply_markup=back_track_name_button()
        )

    elif current_state == TrackNameStates.YEAR_OF_BIRTH.state:
        await state.set_state(TrackNameStates.FIRST_NAME)
        await callback.message.edit_text(
            "Введите инициалы", reply_markup=back_track_name_button()
        )

    elif current_state == TrackNameStates.DISCIPLINE.state:
        await state.set_state(TrackNameStates.YEAR_OF_BIRTH)
        await callback.message.edit_text(
            "Введите год рождения", reply_markup=back_track_name_button()
        )

    elif current_state == TrackNameStates.CUSTOM_DISCIPLINE.state:
        await state.set_state(TrackNameStates.DISCIPLINE)
        await callback.message.edit_text(
            "Выберите спортивную дисциплину", reply_markup=discipline_keyboard()
        )

    await callback.answer()


# Хелпер: показать результат и очистить стейт
async def show_final_result(message: Message, state: FSMContext) -> None:
    result = await get_track_name(state)
    await message.answer(
        f"Результат: {result}", reply_markup=edit_track_name_keyboard()
    )


@track_name_router.callback_query(F.data == "confirm_input")
async def confirm_input(callback: CallbackQuery, state: FSMContext):
    result = await get_track_name(state)
    await state.update_data(track_name=result)
    await search_tracks(callback, state)


async def get_track_name(state):
    data = await state.get_data()
    result = (
        f"{data['second_name']}_{data['first_name']}"
        f"_{data['year_of_birth']}_{data['discipline']}"
    )
    return result
