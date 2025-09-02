import logging


class OwnLoggerFilter(logging.Filter):
    def __init__(self, allowed_loggers_prefixes):
        super().__init__()
        self.allowed_loggers_prefixes = allowed_loggers_prefixes

    def filter(self, record):
        for prefix in self.allowed_loggers_prefixes:
            if record.name.startswith(prefix):
                return True
        return False