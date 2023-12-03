import falcon
import pkg_resources
from prometheus_client import CollectorRegistry, generate_latest, multiprocess

from . import Handler


class MonitoringHandler(Handler):
    """
    Probe handler
    """

    def __init__(self):
        Handler.__init__(self, None)

    def on_get(self, _: falcon.Request, res: falcon.Response):
        try:
            registry = CollectorRegistry()
            multiprocess.MultiProcessCollector(registry)
            data = generate_latest(registry)
            res.content_type = (f'text/plain; version = {pkg_resources.get_distribution("api_test").version}'
                                f'; charset = utf-8')
            res.text = str(data.decode('utf-8'))
        except Exception as err:
            res.text, res.status = self.handle_generic_error(err)
