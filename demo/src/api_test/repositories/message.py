import json

import structlog
from structlog.typing import FilteringBoundLogger

from .errors.repositories_errors import UnknownEntityIdError, DeleteEntityError, UpdateEntityError, CreateEntityError
from ..adapters.errors.postgres_errors import PostgresQueryError
from ..adapters.postgres import Postgres
from ..decorator.logit import logit

ENTITY_NAME: str = 'message'
SELECT_FROM_KEY: str = '''SELECT key, attributes FROM deposit.message WHERE key = %(key)s'''
DELETE_FROM_KEY: str = '''DELETE FROM deposit.message WHERE key = %(key)s'''
UPDATE_FROM_KEY: str = '''UPDATE deposit.message SET attributes = %(attributes)s WHERE key = %(key)s'''
INSERT: str = '''INSERT INTO deposit.message (key, attributes) VALUES (%(key)s, %(attributes)s)'''


class MessageRepository:
    _log: FilteringBoundLogger
    _dal: Postgres

    def __init__(self, dal: Postgres):
        self._dal = dal
        self._log = structlog.get_logger()

    @logit
    def select(self, key: str) -> dict:
        """
        get entity by its key.
        :param key: entity's index key.
        :return: result of query.
        :raise: UnknownEntityIdError: if the entity doesn't exist.
        """
        param = {'key': key}
        result: list = self._dal.exec_read(ENTITY_NAME, SELECT_FROM_KEY, param)
        if len(result) > 0 and result[0][0] == key:
            attributes: dict = result[0][1]
            return {'key': key, 'attributes': attributes}
        else:
            raise UnknownEntityIdError(f'Unknown message entity for key : {key}')

    @logit
    def delete(self, key: str) -> None:
        """
        delete entity by its key.
        :param key: entity's index key.
        :raise: DeleteEntityError: in case of error during the delete operation.
        """
        try:
            param = {'key': key}
            self._dal.exec_write(ENTITY_NAME, DELETE_FROM_KEY, param)
        except PostgresQueryError as err:
            self._log.error(f'Error on delete message entity for key : {key} - {str(err)}')
            raise DeleteEntityError(f'Error on delete message entity for key : {key} - {str(err)}')

    @logit
    def update(self, attributes: dict, key: str) -> None:
        """
        update entity by its key,
        :param attributes: attributes of entity.
        :param key: entity's index key.
        :raise: UpdateEntityError: in case of error during the update operation.
        """
        try:
            param = {'attributes': json.dumps(attributes), 'key': key}
            self._dal.exec_write(ENTITY_NAME, UPDATE_FROM_KEY, param)
        except TypeError as json_err:
            self._log.error(f'Error on update message serialization of attributes for key : {key} - {str(json_err)}')
            raise UpdateEntityError(f'Error on update message serialization of attributes '
                                    f'for key : {key} - {str(json_err)}')
        except PostgresQueryError as err:
            self._log.error(f'Error on update message entity for key : {key} - {str(err)}')
            raise UpdateEntityError(f'Error on update message entity for key : {key} - {str(err)}')

    @logit
    def create(self, attributes: dict, key: str) -> None:
        """
        create entity,
        :param attributes: attributes of entity.
        :param key: entity's index key.
        :raise: UpdateEntityError: in case of error during the update operation.
        """
        try:
            param = {'attributes': json.dumps(attributes), 'key': key}
            self._dal.exec_write(ENTITY_NAME, INSERT, param)
        except TypeError as json_err:
            self._log.error(f'Error on create message serialization of attributes for key : {key} - {str(json_err)}')
            raise CreateEntityError(f'Error on create message serialization of attributes '
                                    f'for key : {key} - {str(json_err)}')
        except PostgresQueryError as err:
            self._log.error(f'Error on create message entity for key : {key} - {str(err)}')
            raise CreateEntityError(f'Error on create message entity for key : {key} - {str(err)}')
