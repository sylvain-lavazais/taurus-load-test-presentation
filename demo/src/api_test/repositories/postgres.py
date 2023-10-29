from contextlib import contextmanager

import psycopg2
import structlog
from psycopg2.extras import DictConnection, DictCursor
from psycopg2.pool import ThreadedConnectionPool
from structlog.typing import FilteringBoundLogger

from .errors.postgres_errors import PostgresConnectionError


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
                 pool_min_connection: int = 2,
                 pool_max_connection: int = 4):
        """
        init a connection repository to postgres with a connection pool

        :param host_name: target database host name
        :param port_number: target TCP port number
        :param database_name: target database name in postgres instance
        :param user_name: target database user
        :param password: user's password
        :param pool_min_connection: minimum connections kept alive in the pool
        :param pool_max_connection: maximum connections kept alive in the pool
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

        if not self.ping_select():
            self._log.critical('cannot connect to database at start-up')
            raise PostgresConnectionError('connection error on postgres repository init')

    def ping_select(self) -> bool:
        """
        emit a simple select query against the database
        :return: a boolean if the request succeeded
        """
        try:
            with self.__db_cursor('ping') as curs:
                curs.execute(Queries.PING_SELECT)

        except psycopg2.Error as pg_error:
            self._log.error(f'error happen during connection test: {pg_error}')
            return False
        return True

    @contextmanager
    def __db_cursor(self, key: str = None) -> DictCursor:
        conn: DictConnection = self._connection_pool.getconn(key)
        try:
            cursor: DictCursor
            with conn.cursor() as cursor:
                yield cursor
        except psycopg2.Error as pg_error:
            self._log.error(f'error happen on getting db cursor with key {key} : {pg_error}')
        finally:
            self._connection_pool.putconn(conn)

    def get_used_connections(self) -> int:
        """ Returns the current database connections used."""
        return len(self._connection_pool._pool)
