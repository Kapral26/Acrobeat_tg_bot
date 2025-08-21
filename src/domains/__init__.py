from src.domains.start.handlers import start_router
from src.domains.tracks.handlers import track_router
from src.domains.tracks.track_name.handlers import track_name_router

routes = [start_router, track_router, track_name_router]
