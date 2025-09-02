import logging

from aiogram import Bot, F, Router
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from src.domains.tracks.service import TrackService
from src.domains.tracks.track_cliper.keyboards import back_period_input_button
from src.domains.tracks.track_cliper.message_cleanup import TrackClipMsgCleanerService
from src.domains.tracks.track_cliper.utils import is_valid_time_format
from src.domains.users.services import UserService

track_cliper_router = Router(name="track_cliper_router")
logger = logging.getLogger(__name__)


class SetClipPeriodStates(StatesGroup):
    PERIOD_START = State()
    PERIOD_END = State()


@track_cliper_router.callback_query(F.data == "set_clip_period")
@inject
async def handler_set_clip_period(
    callback: CallbackQuery,
    bot: Bot,
    state: FSMContext,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
):
    await callback.answer()
    await state.set_state(SetClipPeriodStates.PERIOD_START)
    await _period_start_message(callback, cleaner_service)
    await callback.answer()


async def _period_start_message(
    callback: CallbackQuery, cleaner_service: TrackClipMsgCleanerService
) -> None:
    send_msg = await callback.message.answer(
        """
        ⏱ Укажите время начала обрезки\nПример формата: `мм:сс` → `00:15`
        """,
        reply_markup=await back_period_input_button(),
        parse_mode=ParseMode.MARKDOWN_V2,
    )
    logger.debug(f"Collect mgs_id: {send_msg.message_id} _period_start_message")
    await cleaner_service.collect_cliper_messages_to_delete(
        message_id=send_msg.message_id, user_id=callback.from_user.id
    )
    return


@track_cliper_router.message(SetClipPeriodStates.PERIOD_START)
@inject
async def set_period_start(
    message: Message,
    state: FSMContext,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
) -> None:
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
        reply_markup=await back_period_input_button(),
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


async def show_invalid_time_format_msg(cleaner_service, message):
    send_msg = await message.answer(
        """
        ❌ Неверный формат\nИспользуйте `мм:сс` (например, `01:45`).""",
        reply_markup=await back_period_input_button(),
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
):
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
    state: FSMContext,
    cleaner_service: FromDishka[TrackClipMsgCleanerService],
):
    await cleaner_service.drop_clip_params_message(
        bot=bot, chat_id=callback.message.chat.id, user_id=callback.from_user.id
    )

    await callback.answer()
