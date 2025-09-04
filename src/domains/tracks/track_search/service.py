"""
Модуль `service.py` содержит реализацию сервиса для поиска музыкальных треков.

Обеспечивает функциональность:
- обработки запроса пользователя на поиск;
- отображения результатов поиска в виде inline-клавиатуры;
- управления состоянием FSM (ожидание ввода фразы, подтверждение выбора);
- взаимодействия с сервисами загрузки и сохранения запросов.
"""

import logging
from dataclasses import dataclass

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from src.domains.tracks.keyboards import (
    break_processing,
    get_retry_search_kb,
    kb_track_list,
)
from src.domains.tracks.track_request.service import TrackRequestService
from src.domains.tracks.track_search.states import FindTrackStates
from src.service.downloader.service import DownloaderService

logger = logging.getLogger(__name__)


@dataclass
class TrackSearchService:
    """
    Сервис для поиска музыкальных треков.

    Обрабатывает запросы пользователей, выполняет поиск треков и управляет отображением результатов.
    """

    async def search_tracks(  # noqa: PLR0913
        self,
        callback: CallbackQuery,
        bot: Bot,
        downloader_service: DownloaderService,
        track_request_service: TrackRequestService,
        state: FSMContext,
        query_text: str | None,
    ) -> None:
        """
        Основной метод для поиска треков.

        Если текст запроса предоставлен — выполняет поиск и отображает результаты.
        В противном случае запрашивает у пользователя название трека или исполнителя.

        :param callback: CallbackQuery от нажатия кнопки.
        :param bot: Экземпляр бота Aiogram.
        :param downloader_service: Сервис для загрузки треков.
        :param track_request_service: Сервис для работы с запросами на поиск.
        :param state: Состояние FSM.
        :param query_text: Текст запроса пользователя.
        """
        await callback.answer()

        if query_text:
            await self.handle_search_results(
                bot=bot,
                event=callback.message,
                downloader_service=downloader_service,
                track_request_service=track_request_service,
                query_text=query_text,
                user_id=callback.from_user.id,
                chat_id=callback.message.chat.id,
            )

        else:
            await self.prompt_for_track_name(callback, state)

    @staticmethod
    async def prompt_for_track_name(
        callback: CallbackQuery,
        state: FSMContext,
    ) -> None:
        """
        Запрашивает у пользователя название трека или исполнителя.

        Устанавливает состояние `WAITING_FOR_PHRASE`.

        :param callback: CallbackQuery от нажатия кнопки.
        :param state: Состояние FSM.
        """
        text_search_track = """
            📝 Введи название песни или исполнителя:\n

Например: `«Imagine Dragons — Believer»` или `«Queen»`
        """
        await callback.message.answer(
            text_search_track,
            reply_markup=await break_processing(),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        await state.set_state(FindTrackStates.WAITING_FOR_PHRASE)

    async def handle_search_results(  # noqa: PLR0913
        self,
        bot: Bot,
        event: CallbackQuery | Message,
        downloader_service: DownloaderService,
        track_request_service: TrackRequestService,
        query_text: str,
        user_id: int,
        chat_id: int,
        skip_repo_alias: str | None = None,
    ) -> None:
        """
        Обрабатывает результаты поиска треков и отображает их пользователю.

        :param bot: Экземпляр бота Aiogram.
        :param event: Событие (CallbackQuery или Message).
        :param downloader_service: Сервис для загрузки треков.
        :param track_request_service: Сервис для работы с запросами на поиск.
        :param query_text: Текст запроса пользователя.
        :param user_id: ID пользователя.
        :param chat_id: ID чата.
        :param skip_repo_alias: Алиас репозитория, который нужно пропустить при поиске.
        """
        try:
            await track_request_service.insert_track_request(
                user_id=user_id,
                query_text=query_text,
            )

            find_tracks = await downloader_service.find_tracks_on_phrase(
                phrase=query_text,
                bot=bot,
                chat_id=chat_id,
                skip_repo_alias=skip_repo_alias,
            )

            if not find_tracks:
                await self.show_no_tracks_found(event)
                return

            message_text = f"""
            🎵 Нашёл несколько вариантов:\nВыбери подходящую песню из списка:
            \n\n[Источник: {find_tracks.repo_alias}]
            """
            keyboard = await kb_track_list(find_tracks)

            if isinstance(event, CallbackQuery) and event.message:
                await event.message.edit_text(
                    message_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )
            else:
                await event.answer(
                    message_text,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

        except Exception as e:
            logger.exception(f"Ошибка при обработке результатов поиска: {e}")  # noqa: TRY401
            await self.show_error_message(event)

    @staticmethod
    async def show_no_tracks_found(
        event: CallbackQuery | Message,
    ) -> None:
        """
        Отправляет сообщение о том, что треки не найдены.

        :param event: Событие (CallbackQuery или Message).
        """
        message = event.message if isinstance(event, CallbackQuery) else event
        await message.edit_text(
            "😔 Песни не найдены.\nПопробуйте что-то другое или уточните поисковой запрос.",
            reply_markup=await get_retry_search_kb(),
        )

    @staticmethod
    async def show_error_message(
        event: CallbackQuery | Message,
    ) -> None:
        """
        Отправляет сообщение об ошибке.

        :param event: Событие (CallbackQuery или Message).
        """
        message = event.message if isinstance(event, CallbackQuery) else event
        await message.edit_text(
            "⚠️ Произошла ошибка.\n Попробуйте позже.",
            reply_markup=await get_retry_search_kb(),
        )
