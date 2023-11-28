import time

import falcon
import structlog

from ..commons.metrics import Metrics


class Prometheus:
    def __init__(self, prometheus: Metrics):
        self._excluded_resources = (
                '/_private/_liveness',
                '/_private/_readiness',
                '/_private/_metrics'
                '/_health',
        )
        self._logger = structlog.get_logger('falcon')
        self._prometheus = prometheus

    def process_request(self, req: falcon.Request, _: falcon.Response):
        """Process the request before routing it.

        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().

        :param _: Response object that will be routed to the on_* responder. (ignored)
        :param req: Request object that will eventually be routed to an on_* responder method.
        """
        req.start_time = time.time()

    def process_response(self, req: falcon.Request, resp: falcon.Response, _, __):
        """
        Post-processing of the response (after routing)
        :param req:
        :param resp:
        :param _: Resource object to which the request was routed. May
            be None if no route was found for the request.
        :param __: True if no exceptions were raised while the
            framework processed and routed the request; otherwise False.
        :return:
        """
        resp_time = time.time() - req.start_time

        self._prometheus.requests.labels(method=req.method, path=req.path,
                                         status=resp.status).inc()
        self._prometheus.request_historygram.labels(
                method=req.method,
                path=req.path,
                status=resp.status,
        ).observe(resp_time)
