import os
from contextlib import contextmanager
from typing import List

import psycopg2
import structlog
from psycopg2.extras import DictConnection, DictCursor, DictRow
from psycopg2.pool import ThreadedConnectionPool
from structlog.typing import FilteringBoundLogger
from yoyo import get_backend, read_migrations

from .. import db
from .errors.postgres_errors import (
    PostgresConnectionError,
    PostgresCursorError,
    PostgresQueryError,
)


class Queries:
    PING_SELECT: str = "SELECT 1"


class Postgres:
    """
    Postgres Data Access Repository.
    """
    _log: FilteringBoundLogger
    _db_name: str
    _db_user: str
    _db_password: str
    _db_host: str
    _db_port: str


    def __init__(self,
                 host_name: str,
                 port_number: int,
                 database_name: str,
                 user_name: str,
                 password: str,
                 migration_folder: str = os.path.dirname(os.path.abspath(db.__file__))):
        """
        init a connection repository to postgres with a connection pool

        :param host_name: target database host name
        :param port_number: target TCP port number
        :param database_name: target database name in postgres instance
        :param user_name: target database user
        :param password: user's password
        :param migration_folder: database migration script folder (default = db package file path)
        :param pool_min_connection: minimum connections kept alive in the pool (default = 2)
        :param pool_max_connection: maximum connections kept alive in the pool (default = 4)
        :raise PostgresConnectionError: on init of the class if the connection can't be established
        """
        self._db_name = database_name
        self._db_user = user_name
        self._db_password = password
        self._db_host = host_name
        self._db_port = port_number

        self._log = structlog.get_logger()

        self._log.debug('init postgres repository')

        self.ping_select()
        self.__apply_migration(host_name,
                               port_number,
                               database_name,
                               user_name,
                               password,
                               migration_folder)

    def __apply_migration(self,
                          db_host: str,
                          db_port: int,
                          db_name: str,
                          db_user: str,
                          db_password: str,
                          migration_folder: str):
        try:
            self._log.debug('applying yoyo migration')
            connection_string: str = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            backend = get_backend(connection_string)
            self._log.debug(f'applying migration files in {migration_folder}')
            self._log.debug(f'on connection {connection_string}')
            migrations = read_migrations(migration_folder)
            backend.apply_migrations(backend.to_apply(migrations))
        except Exception as error:
            self._log.critical(f'cannot connect to database at start-up: {error}')
            raise PostgresConnectionError('connection error on postgres repository init')

    def ping_select(self):
        """
        emit a simple select query against the database
        :raise PostgresConnectionError connection error on simple select
        """

        self.exec_read('ping', Queries.PING_SELECT)

    def exec_read(self, entity: str, query: str, params: dict = None) -> List[DictRow]:
        """
        execute a read query on postgres database
        :param entity: entity that will be queried ((or a scope, if there are more than one)
        :param query: query to be executed
        :param params: optional parameter to fulfill the query
        :return: list of DictRow
        """
        log_query = query.replace('\n', '')
        try:
            with self.__db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as curs:
                    curs.execute(query, params)
                    self._log.debug(f'executing query [{log_query}]')
                    self._log.debug(f'with param [{params}]')
                    return curs.fetchall()
        except psycopg2.Error as error:
            self._log.warn(f'Error occur on read of {log_query} - {error}')

    def exec_write(self, entity: str, query: str, params: dict) -> None:
        """
        execute a writing query on postgres database
        :param entity: entity that will be queried (or a scope, if there are more than one)
        :param query: query to be executed
        :param params: optional parameter to fulfill the query
        :raise PostgresQueryError: on error during writing process
        """
        log_query = query.replace('\n', '')
        try:
            with self.__db_connection() as conn:
                with conn.cursor(cursor_factory=DictCursor) as curs:
                    curs.execute(query, params)
                    self._log.debug(f'executing query [{log_query}]')
                conn.commit()
        except psycopg2.Error as error:
            self._log.error(f'Error occur on write of {log_query} - {error}')
            conn.rollback()
            raise PostgresQueryError(f'Error occur on write of {log_query} - {error}')

    def __db_connection(self):
        try:
            params = {
                    'database': self._db_name,
                    'user'    : self._db_user,
                    'password': self._db_password,
                    'host'    : self._db_host,
                    'port'    : self._db_port
            }
            return psycopg2.connect(**params)
        except (Exception, psycopg2.DatabaseError) as error:
            self._log.critical(f'Error occur on connection to database - \n {error}')

