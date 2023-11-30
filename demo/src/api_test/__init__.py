import logging
import multiprocessing
import os

import click
import falcon
import gunicorn.app.base
import pkg_resources
import structlog as structlog
from dynaconf import Dynaconf, LazySettings
from falcon import App
from structlog.typing import FilteringBoundLogger

from .commons.metrics import Metrics
from .handlers.health import HealthHandler, ReadinessHandler, LivenessHandler
from .handlers.message import MessageKeyHandler, MessageHandler
from .handlers.monitoring import MonitoringHandler
from .middlewares.prometheus import Prometheus
from .middlewares.telemetry import Telemetry
from .middlewares.tracking_id import TrackingId
from .adapters.postgres import Postgres
from .repositories.message import MessageRepository
from .services.health import HealthService
from .services.message import MessageService


class APITest:
    _message_service: MessageService
    _health_service: HealthService
    _log: FilteringBoundLogger
    _settings: LazySettings

    def __init__(self, log_level: str, config_file: str):
        self.__init_logger(log_level)
        self._log = structlog.get_logger()

        self._settings = self.__init_configuration(config_file)
        dal = self.__init_database(self._settings)

        self._health_service = HealthService(dal, self._settings)
        self._message_service = MessageService(MessageRepository(dal))

    def __init_database(self, settings: LazySettings) -> Postgres:
        self._log.debug(f'Initialize Database component on {settings.db_host_name} - Start')
        dal: Postgres = Postgres(settings.db_host_name,
                                 settings.db_port_number,
                                 settings.db_database_name,
                                 settings.db_user_name,
                                 settings.db_user_password,
                                 pool_min_connection=settings.db_pool_min_connection,
                                 pool_max_connection=settings.db_pool_max_connection)
        self._log.debug(f'Initialize Database component on {settings.db_host_name} - Done')
        return dal

    def __init_configuration(self, config_file: str) -> LazySettings:
        self._log.debug('Initialize Configuration component - Start')
        settings = Dynaconf(settings_file=config_file,
                            envvar_prefix='API',
                            environments=True,
                            load_dotenv=True,
                            default_env='default',
                            env=os.getenv('API_ENV', 'dev'))
        self._log.debug('Initialize Configuration component - Done')
        return settings

    def __init_logger(self, log_level):
        structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(
                        logging.getLevelName(log_level)),
        )

    def router(self) -> App:
        """
        Initialize the falcon api and router
        :return: App managed by Falcon
        """
        # router with middleware (for metrics and request tracking)
        metrics = Metrics()
        router = falcon.App(middleware=[Prometheus(metrics), Telemetry(), TrackingId()],
                            media_type=falcon.MEDIA_JSON)

        if not self._settings.debug_mode:
            self._health_service.start()
            # health routes
            router.add_route('/_health', HealthHandler(self._health_service))
            router.add_route('/_private/_readiness', ReadinessHandler(self._health_service))
            router.add_route('/_private/_liveness', LivenessHandler(self._health_service))
            router.add_route('/_private/_metrics', MonitoringHandler())

        # Message
        # GET, PUT, DELETE
        router.add_route('/message/{key}', MessageKeyHandler(self._message_service))
        router.add_route('/message', MessageHandler(self._message_service))
        # GET TODO: implement handler
        # router.add_route('/messages', MessageKeyHandler(self._message_service))

        return router


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app: App, options: dict = None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self) -> App:
        return self.application


@click.command()
@click.argument('hostname')
@click.argument('port')
@click.option('--config_file', default='./config.toml',
              help='set the application configuration file path (default = ./config.toml')
@click.option('--log_level', default='INFO',
              help='set the logger level, choose between [CRITICAL / ERROR / WARNING / INFO / DEBUG] (default = INFO)')
@click.option('--worker_nb', default=number_of_workers(),
              help='set the number of worker for the web application (default = cpu core count x 2 + 1)')
def command_line(hostname: str,
                 port: str,
                 config_file: str,
                 log_level: str,
                 worker_nb: int):
    """\b
    Start the api-test application
    \b
    Usage:
    api-test [Options] hostname port
    """

    print(f'=== {APITest.__name__} - {pkg_resources.get_distribution("api_test").version} ===')

    options = {
            'bind'        : '%s:%s' % (hostname, port),
            'workers'     : worker_nb,
            'threads'     : '30',
            'keepalive'   : '2',
            'timeout'     : '120',
            'worker_class': 'gthread',
            'logger_class': 'api_test.commons.gunicorn_logger.GunicornLogger'
    }

    app: APITest = APITest(log_level, config_file)
    std_app = StandaloneApplication(app.router(), options)
    std_app.run()
