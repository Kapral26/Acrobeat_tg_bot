from src.domains.start import start_router
from src.domains.tracks import track_router
from src.domains.tracks.track_name import track_name_router

routes = [start_router, track_router, track_name_router]
