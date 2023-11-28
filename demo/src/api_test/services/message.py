from typing import Any, Dict, Tuple, List

import structlog
from structlog.typing import FilteringBoundLogger

from ..repositories.errors.repositories_errors import UnknownEntityIdError
from ..repositories.message import MessageRepository


class MessageService:
    _log: FilteringBoundLogger
    _repo: MessageRepository

    def __init__(self, repository: MessageRepository):
        self._log = structlog.get_logger()
        self._repo = repository

    def read(self, key: str) -> Tuple[List[Dict[str, dict]], List[Dict[str, str]]]:
        try:
            data: Dict[str, dict] = self._repo.select(key)
            return [data], []
        except UnknownEntityIdError as unknown:
            return [], [{'error_code': {'UNKNOWN': 'entity unknown'}, 'error': str(unknown)}]
