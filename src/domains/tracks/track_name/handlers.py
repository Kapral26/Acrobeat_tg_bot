from aiogram import F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from src.domains.tracks.handlers import search_tracks
from src.domains.tracks.track_name import track_name_router
from src.domains.tracks.track_name.keyboards import (
    back_track_name_button,
    discipline_keyboard,
    edit_track_name_keyboard,
)


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
    await state.update_data(second_name=message.text)
    await state.set_state(TrackNameStates.FIRST_NAME)
    await message.answer("Введите инициалы", reply_markup=back_track_name_button())


@track_name_router.message(TrackNameStates.FIRST_NAME)
async def set_year_of_birth(message: Message, state: FSMContext) -> None:
    """
    Обработчик ввода инициалов.
    Сохраняет инициалы и переходит к следующему шагу — вводу года рождения.

    Аргументы:
        message (Message): Сообщение от пользователя.
        state (FSMContext): Контекст машины состояний.
    """
    await state.update_data(first_name=message.text)
    await state.set_state(TrackNameStates.YEAR_OF_BIRTH)
    await message.answer("Введите год рождения", reply_markup=back_track_name_button())


@track_name_router.message(TrackNameStates.YEAR_OF_BIRTH)
async def choose_discipline(message: Message, state: FSMContext) -> None:
    await state.update_data(year_of_birth=message.text)
    await state.set_state(TrackNameStates.DISCIPLINE)
    await message.answer(
        "Выберите спортивную дисциплину", reply_markup=discipline_keyboard()
    )


@track_name_router.callback_query(F.data.startswith("discipline:"))
async def process_discipline(callback: CallbackQuery, state: FSMContext) -> None:
    value = callback.data.split(":", 1)[1]

    if value == "custom":
        await state.set_state(TrackNameStates.CUSTOM_DISCIPLINE)
        await callback.message.edit_text(
            "Введите дисциплину вручную", reply_markup=back_track_name_button()
        )
    else:
        await state.update_data(discipline=value)
        await show_final_result(callback.message, state)
        await callback.answer()


@track_name_router.message(TrackNameStates.CUSTOM_DISCIPLINE)
async def set_custom_discipline(message: Message, state: FSMContext) -> None:
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
