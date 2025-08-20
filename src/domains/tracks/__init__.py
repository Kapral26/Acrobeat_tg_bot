from aiogram import Router

track_router = Router(name="track_router")

from src.domains.tracks import handlers
