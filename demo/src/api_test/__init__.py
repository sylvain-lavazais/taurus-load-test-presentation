import logging
import multiprocessing

import click
import falcon
import pkg_resources
import gunicorn
import structlog as structlog

from .common.metrics import Metrics
from .handlers.health import HealthHandler, ReadinessHandler, LivenessHandler
from .handlers.monitoring import MonitoringHandler
from .middleware.prometheus import Prometheus
from .middleware.telemetry import Telemetry
from .middleware.tracking_id import TrackingId


class APITest:

    def __init__(self, log_level: str):
        structlog.configure(
                wrapper_class=structlog.make_filtering_bound_logger(
                        logging.getLevelName(log_level)),
        )

    def get_API(self) -> falcon.API:
        """
        Initialize the falcon api and our router
        """
        # resources = []
        #
        # service_orchestrator = Orchestrator()
        #
        # # Create our WSGI application
        # # media_type set for json:api compliance
        metrics = Metrics()
        router = falcon.API(middleware=[Prometheus(metrics), Telemetry(), TrackingId()],
                            media_type=falcon.MEDIA_JSON)
        #
        # if not util.strtobool(str(settings.APP_DEBUG)):
        #     health_service = initialize_health(service_orchestrator.dal)
        # health routes
        router.add_route('/_health', HealthHandler(health_service))
        router.add_route('/_private/_readiness', ReadinessHandler(health_service))
        router.add_route('/_private/_liveness', LivenessHandler(health_service))
        router.add_route('/_private/_metrics', MonitoringHandler())
        #
        # # public routes
        # message_resource = MessageResource(service_orchestrator)
        # topic_resource = TopicResource(service_orchestrator)
        #
        # resources.append(message_resource)
        # resources.append(topic_resource)
        #
        # router.add_route('/messages', message_resource)
        # router.add_route('/topics', topic_resource)
        #
        # spec_resource = SwaggerResource(api_app=router, resources=resources)
        # router.add_route('/swagger', spec_resource)

        return router


def number_of_workers():
    return (multiprocessing.cpu_count() * 2) + 1


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app: falcon.API, options: dict = None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items()
                  if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application


@click.command()
@click.argument('hostname')
@click.argument('port')
@click.option('--config', default='./app_config.toml',
              help='set the application configuration file path (default = ./app_config.toml')
@click.option('--log_level', default='INFO',
              help='set the logger level, choose between [CRITICAL / ERROR / WARNING / INFO / DEBUG] (default = INFO)')
@click.option('--worker_nb', default=(multiprocessing.cpu_count() * 2) + 1,
              help='set the number of worker for the web application')
def command_line(hostname: str,
                 port: str,
                 log_level: str,
                 worker_nb: int):
    """\b
    Start the api-test application
    \b
    Usage :
    api-test [Options] hostname port
    \b
    list of arguments
       : import scratch configurations from AWX
    sync     : sync local configuration with AWX
    validate : only validate configuration file (default)
    migrate  : migrate current configuration to another environment
    version  : display the current version of awx-synchronizer
    """

    print(f'=== {APITest.__name__} - {pkg_resources.get_distribution("api_test").version} ===')

    options = {
            'bind'        : '%s:%s' % (hostname, port),
            'workers'     : worker_nb,
            'threads'     : '30',
            'keepalive'   : '2',
            'timeout'     : '120',
            'worker_class': 'eventlet',
            'logger_class': 'api_test.common.gunicorn_logger.Logger'
    }
