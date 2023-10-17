import falcon
from prometheus_client import generate_latest, CollectorRegistry, multiprocess

from mirror_reader.handler.handler import Handler


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
            res.content_type = 'text/plain; version = 0.0.4; charset = utf-8'
            res.body = str(data.decode('utf-8'))
        except Exception as err:
            res.body, res.status = self.handle_generic_error(err)
