from typing import List

import structlog
from psycopg2.extras import DictRow
from structlog.typing import FilteringBoundLogger

from .errors.repositories_errors import UnknownEntityIdError
from ..adapters.postgres import Postgres
from ..decorator.logit import logit

ENTITY_NAME: str = 'message'
SELECT_FROM_KEY: str = '''SELECT key, attributes FROM deposit.message WHERE key = %(key)s'''


class MessageRepository:
    _log: FilteringBoundLogger
    _dal: Postgres

    def __init__(self, dal: Postgres):
        self._dal = dal
        self._log = structlog.get_logger()

    @logit
    def select(self, key: str) -> dict:
        param = {'key': key}
        result: list = self._dal.exec_read(ENTITY_NAME, SELECT_FROM_KEY, param)
        if len(result) > 0 and result[0][0] == key:
            attributes: dict = result[0][1]
            return {'key': key, 'attributes': attributes}
        else:
            self._log.warn(f'Unknown message entity for key : {key}')
            raise UnknownEntityIdError(f'Unknown message entity for key : {key}')
