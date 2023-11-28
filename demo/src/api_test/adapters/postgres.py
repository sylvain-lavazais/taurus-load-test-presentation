import os
from contextlib import contextmanager
from typing import List

import psycopg2
import structlog
from psycopg2.extras import DictConnection, DictCursor, DictRow
from psycopg2.pool import ThreadedConnectionPool
from structlog.typing import FilteringBoundLogger
from yoyo import get_backend, read_migrations

from .errors.postgres_errors import PostgresConnectionError, PostgresCursorError
from .. import db


class Queries:
    PING_SELECT: str = "SELECT 1"


class Postgres:
    """
    Postgres Data Access Repository.
    """
    _connection_pool: ThreadedConnectionPool
    _log: FilteringBoundLogger

    def __init__(self,
                 host_name: str,
                 port_number: int,
                 database_name: str,
                 user_name: str,
                 password: str,
                 migration_folder: str = os.path.dirname(os.path.abspath(db.__file__)),
                 pool_min_connection: int = 2,
                 pool_max_connection: int = 4):
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
        self._log = structlog.get_logger()

        self._log.debug('init postgres repository')

        # List of Kwargs passed in pools connection
        #     - *dbname*: the database name
        #     - *database*: the database name (only as keyword argument)
        #     - *user*: user name used to authenticate
        #     - *password*: password used to authenticate
        #     - *host*: database host address (defaults to UNIX socket if not provided)
        #     - *port*: connection port number (defaults to 5432 if not provided)

        self._connection_pool = ThreadedConnectionPool(pool_min_connection,
                                                       pool_max_connection,
                                                       database=database_name,
                                                       user=user_name,
                                                       password=password,
                                                       host=host_name,
                                                       port=port_number)

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
            backend = get_backend(f'postgresql://{db_user}:{db_password}@'
                                  f'{db_host}:{db_port}/{db_name}')
            self._log.debug(f'applying migration files in {migration_folder}')
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
        with self.__connection(f'read-{entity}') as conn:
            try:
                with self.__cursor(conn) as curs:
                    curs.execute(query, params)
                    self._log.debug(f'executing query [{log_query}]')
                    self._log.debug(f'with param [{params}]')
                    return curs.fetchall()
            except psycopg2.Error as error:
                self._log.warn(f'Error occur on read of {log_query} - {error}')
            finally:
                self._connection_pool.putconn(conn)

    def exec_db_write(self, entity: str, query: str, params: dict) -> None:
        """
        execute a writing query on postgres database
        :param entity: entity that will be queried (or a scope, if there are more than one)
        :param query: query to be executed
        :param params: optional parameter to fulfill the query
        """
        log_query = query.replace('\n', '')
        with self.__connection(f'write-{entity}') as conn:
            try:
                with self.__cursor(conn) as curs:
                    curs.execute(query, params)
                    self._log.debug(f'executing query [{log_query}]')
                conn.commit()
            except psycopg2.Error as error:
                self._log.error(f'Error occur on write of {log_query} - {error}')
                conn.rollback()
            finally:
                self._connection_pool.putconn(conn)

    @contextmanager
    def __connection(self, key: str) -> DictConnection:
        try:
            conn: DictConnection
            with self._connection_pool.getconn(key) as conn:
                yield conn
        except psycopg2.Error as pg_error:
            self._log.critical(f'error happen on getting db connection with key {key} : {pg_error}')
            raise PostgresConnectionError(f'getting db connection with key {key} : {pg_error}')

    @contextmanager
    def __cursor(self, conn: DictConnection) -> DictCursor:
        try:
            cursor: DictCursor
            with conn.cursor() as cursor:
                yield cursor
        except psycopg2.Error as pg_error:
            self._log.critical(f'error happen on getting db cursor : {pg_error}')
            raise PostgresCursorError(f'getting db cursor : {pg_error}')

    def get_used_connections(self) -> int:
        """ Returns the current database connections used."""
        return len(self._connection_pool._pool)
