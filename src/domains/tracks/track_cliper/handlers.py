"""
Модуль `handlers.py` содержит обработчики событий для взаимодействия с вводом временных параметров аудиообрезки.

Обрабатывает:
- инициацию ввода временных меток (начало и конец обрезки);
- валидацию формата времени;
- переход между этапами ввода;
- повторную обработку трека после коррекции параметров.
"""

import logging

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.service import TrackService
from src.domains.tracks.track_cliper.keyboards import kb_back_period_input
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.utils import is_valid_time_format
from src.domains.users.services import UserService

track_cliper_router = Router(name="track_cliper_router")
logger = logging.getLogger(__name__)


class SetClipPeriodStates(StatesGroup):
    """
    Группа состояний для процесса ввода временных параметров обрезки трека.

    Описывает этапы:
    - ввод времени начала обрезки;
    - ввод времени окончания обрезки.
    """

    PERIOD_START = State()
    PERIOD_END = State()


@track_cliper_router.callback_query(F.data == "set_clip_period")
@inject
async def handler_set_clip_period(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
) -> None:
    """
    Обработчик для инициации ввода временных параметров обрезки.

    Устанавливает начальное состояние (`PERIOD_START`) и запрашивает у пользователя время начала обрезки.

    :param callback: CallbackQuery от нажатия кнопки "Обрезать трек".
    :param bot: Экземпляр бота Aiogram.
    :param state: Состояние FSM для управления диалогом.
    :param cleaner_service: Сервис для управления временными сообщениями.
    """
    await callback.answer()
    await state.set_state(SetClipPeriodStates.PERIOD_START)
    await _period_start_message(callback, cleaner_service)
    await callback.answer()


async def _period_start_message(
    callback: CallbackQuery, cleaner_service: TrackClipMsgCleanerService
) -> None:
    """
    Вспомогательная функция для отправки запроса на ввод времени начала обрезки.

    Отправляет сообщение с примером формата времени и регистрирует его для последующей очистки.

    :param callback: CallbackQuery от пользователя.
    :param cleaner_service: Сервис для управления временными сообщениями.
    """
    send_msg = await callback.message.answer(
        """
        ⏱ Укажите время начала обрезки\nПример формата: `мм:сс` → `00:15`
        """,
        reply_markup=await kb_back_period_input(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.debug(f"Collect mgs_id: {send_msg.message_id} _period_start_message")
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=send_msg.message_id, user_id=callback.from_user.id
    )


@track_cliper_router.message(SetClipPeriodStates.PERIOD_START)
@inject
async def set_period_start(
    message: Message,
    state: FSMContext,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
) -> None:
    """
    Обработчик ввода времени начала обрезки.

    Проверяет корректность формата времени и переходит к вводу времени окончания.
    При некорректном формате отправляет сообщение об ошибке.

    :param message: Сообщение от пользователя с временем начала.
    :param state: Состояние FSM для управления диалогом.
    :param cleaner_service: Сервис для управления временными сообщениями.
    """
    periodic_start = message.text.strip()
    logger.debug(f"Collect mgs_id: {message.message_id} set_period_start")
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=message.message_id, user_id=message.from_user.id
    )
    if not is_valid_time_format(periodic_start):
        await show_invalid_time_format_msg(cleaner_service, message)
        return

    await state.update_data(period_start=periodic_start)
    await state.set_state(SetClipPeriodStates.PERIOD_END)

    send_msg = await message.answer(
        """
        ⏱ Укажите время окончания обрезки\nФормат: `мм:сс` → пример `01:19`""",
        reply_markup=await kb_back_period_input(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.debug(f"Collect mgs_id: {send_msg.message_id} msg_end_period")
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=send_msg.message_id, user_id=message.from_user.id
    )


@track_cliper_router.message(SetClipPeriodStates.PERIOD_END)
@inject
async def set_period_end(
    message: Message,
    bot: Bot,
    state: FSMContext,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
    track_service: FromDishka[TrackService],
    user_service: FromDishka[UserService],
) -> None:
    """
    Обработчик ввода времени окончания обрезки.

    Проверяет корректность формата времени, сохраняет данные и запускает обработку трека.
    При некорректном формате отправляет сообщение об ошибке.

    :param message: Сообщение от пользователя с временем окончания.
    :param bot: Экземпляр бота Aiogram.
    :param state: Состояние FSM для управления диалогом.
    :param cleaner_service: Сервис для управления временными сообщениями.
    :param track_service: Сервис для работы с аудиофайлами.
    :param user_service: Сервис для работы с пользователями.
    """
    time_str = message.text.strip()
    logger.debug(f"Collect mgs_id: {message.message_id} set_period_end")
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=message.message_id, user_id=message.from_user.id
    )
    if not is_valid_time_format(time_str):
        await show_invalid_time_format_msg(cleaner_service, message)
        return

    await state.update_data(period_end=time_str)
    state_data = await state.get_data()
    track_name = await user_service.get_session_track_name(message.from_user.id)
    await track_service.download_clipped_track(
        track_path=state_data["track_path"],
        track_name=track_name,
        bot=bot,
        chat_id=message.chat.id,
        state=state,
        user_id=message.from_user.id,
    )


async def show_invalid_time_format_msg(
    cleaner_service: TrackClipMsgCleanerService,
    message: Message,
) -> None:
    """
    Отправляет сообщение об ошибке при некорректном формате времени.

    Регистрирует сообщение для последующей очистки.

    :param cleaner_service: Сервис для управления временными сообщениями.
    :param message: Сообщение от пользователя.
    """
    send_msg = await message.answer(
        """
        ❌ Неверный формат\nИспользуйте `мм:сс` (например, `01:45`).""",
        reply_markup=await kb_back_period_input(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=send_msg.message_id, user_id=send_msg.from_user.id
    )


@track_cliper_router.callback_query(F.data == "go_back_clip_period_item")
@inject
async def go_back(
    callback: CallbackQuery,
    state: FSMContext,
    bot: Bot,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
) -> None:
    """
    Обработчик кнопки "Назад" для перехода между этапами ввода временных параметров.

    Управляет возвратом к предыдущему этапу (время начала или удаление текущего сообщения).

    :param callback: CallbackQuery от нажатия кнопки "Назад".
    :param state: Состояние FSM для управления диалогом.
    :param bot: Экземпляр бота Aiogram.
    :param cleaner_service: Сервис для управления временными сообщениями.
    """
    current_state = await state.get_state()

    if current_state == SetClipPeriodStates.PERIOD_END.state:
        await _period_start_message(callback, cleaner_service)
        await state.set_state(SetClipPeriodStates.PERIOD_START)
    elif current_state == SetClipPeriodStates.PERIOD_START.state:
        await bot.delete_message(callback.message.chat.id, callback.message.message_id)

    await callback.answer()


@track_cliper_router.callback_query(F.data == "clip_track_again")
@inject
async def clip_track_again(
    callback: CallbackQuery,
    bot: Bot,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
) -> None:
    """
    Обработчик для повторной обработки трека после коррекции параметров.

    Очищает временные сообщения и позволяет пользователю заново ввести временные параметры.

    :param callback: CallbackQuery от нажатия кнопки "Повторить обработку".
    :param bot: Экземпляр бота Aiogram.
    :param cleaner_service: Сервис для управления временными сообщениями.
    """
    await cleaner_service.drop_clip_params_message(
        bot=bot, chat_id=callback.message.chat.id, user_id=callback.from_user.id
    )

    await callback.answer()
