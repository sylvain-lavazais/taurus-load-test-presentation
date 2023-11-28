from structlog.typing import FilteringBoundLogger

from ..repositories.postgres import Postgres


class MessageService:
    _log: FilteringBoundLogger
    _dal: Postgres

    def __init__(self):
        pass
