from datetime import datetime

import falcon
import structlog


class Telemetry:
    def __init__(self):
        self._logger = structlog.get_logger('falcon')
        self._excluded_resources = (
                '/_health',
                '/_private/_liveness',
                '/_private/_readiness',
                '/_private/_metrics',
        )

    def process_request(self, req: falcon.Request, _: falcon.Response) -> None:
        """Process the request before routing it.

        Note:
            Because Falcon routes each request based on req.path, a
            request can be effectively re-routed by setting that
            attribute to a new value from within process_request().

        :param _: Response object that will be routed to the on_* responder. (Ignored)
        :param req: Request object that will eventually be routed to an on_* responder method.
        """
        if req.path not in self._excluded_resources:
            req.context['received_at'] = datetime.now()
            self._logger.info("Request received",
                              http={
                                      'method'     : req.method,
                                      'url_details': {
                                              'path'       : req.path,
                                              'host'       : req.netloc,
                                              'queryString': req.params,
                                              'scheme'     : req.scheme
                                      }
                              })

    def process_response(self, req: falcon.Request, resp: falcon.Response, _, __) -> None:
        """
        Post-processing of the response (after routing)
        :param req:
        :param resp:
        :param resource: Resource object to which the request was routed. May
            be None if no route was found for the request.
        :param req_succeeded: True if no exceptions were raised while the
            framework processed and routed the request; otherwise False.
        :return:
        """
        if req.path not in self._excluded_resources:
            status = 0
            try:
                status = int(resp.status[0:3])
            except Exception:
                pass  # intentionally ignore

            duration_time = int(
                    (datetime.now() - req.context['received_at']).total_seconds() * 1000000)
            self._logger.info("Request completed",
                              http={
                                      'method'     : req.method,
                                      'url_details': {
                                              'path'       : req.path,
                                              'host'       : req.netloc,
                                              'queryString': req.params,
                                              'scheme'     : req.scheme,
                                              'status_code': status
                                      }
                              },
                              duration=duration_time)
