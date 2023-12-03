from typing import Dict, List, Tuple

import structlog
from structlog.typing import FilteringBoundLogger

from ..repositories.errors.repositories_errors import (
    CreateEntityError,
    DeleteEntityError,
    UnknownEntityIdError,
    UpdateEntityError,
)
from ..repositories.message import MessageRepository

ENTITY_ALREADY_EXIST: str = 'entity already exist'


class MessageService:
    _log: FilteringBoundLogger
    _repo: MessageRepository

    def __init__(self, repository: MessageRepository):
        self._log = structlog.get_logger()
        self._repo = repository

    def read(self, key: str) -> Tuple[List[Dict[str, dict]], List[Dict[str, str]]]:
        """
        Read a Message by its key
        :param key: message's key
        :return: tuple of data and error (if error is not empty, data will be empty)
        """
        try:
            data: Dict[str, dict] = self._repo.select(key)
            return [data], []
        except UnknownEntityIdError as unknown:
            return [], [{'error_code': {'UNKNOWN': 'entity unknown'}, 'error': str(unknown)}]

    def delete(self, key: str) -> List[Dict[str, str]]:
        """
        Delete a Message by its key
        :param key: message's key
        :return: error dict (if it empty, everything works)
        """
        try:
            message = self._repo.select(key)
            self._repo.delete(message['key'])
        except UnknownEntityIdError as unknown:
            return [{'error_code': {'UNKNOWN': 'entity unknown'}, 'error': str(unknown)}]
        except DeleteEntityError as delete:
            return [{'error_code': {'DELETE': 'deletion error'}, 'error': str(delete)}]
        return []

    def update(self, attributes: dict, key: str) -> List[Dict[str, str]]:
        """
        Update a Message by its key
        :param key: message's key
        :param attributes: message's attributes
        :return: error dict (if its empty, everything works)
        """
        try:
            message = self._repo.select(key)
            self._repo.update(attributes, message['key'])
        except UnknownEntityIdError as unknown:
            return [{'error_code': {'UNKNOWN': 'entity unknown'}, 'error': str(unknown)}]
        except UpdateEntityError as update:
            return [{'error_code': {'UPDATE': 'update error'}, 'error': str(update)}]
        return []

    def create(self, attributes: dict, key: str) -> List[Dict[str, str]]:
        """
        Create a Message by its key and attributes
        :param key: message's key
        :param attributes: message's attributes
        :return: error dict (if its empty, everything works)
        """
        try:
            message = self._repo.select(key)
            if 'key' in message:
                return [{'error_code': {'CREATE': ENTITY_ALREADY_EXIST}, 'error': f'message already {key} exist'}]
        except UnknownEntityIdError:
            self._repo.create(attributes, key)
        except CreateEntityError as create:
            return [{'error_code': {'CREATE': 'creation error'}, 'error': str(create)}]
        return []
