from src.domains.start.handlers import start_router
from src.domains.tracks.handlers import track_router
from src.domains.tracks.track_cliper.handlers import track_cliper_router
from src.domains.tracks.track_name.handlers import track_name_router
from src.domains.tracks.track_request.handlers import track_request_router
from src.domains.tracks.track_search.handlers import track_search_router

routes = [
    start_router,
    track_router,
    track_name_router,
    track_request_router,
    track_cliper_router,
    track_search_router,
]
