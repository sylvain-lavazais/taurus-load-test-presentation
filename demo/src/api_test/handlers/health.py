from falcon import HTTP_200, HTTP_503, request, response, Response, Request, HTTP_204
from structlog.typing import FilteringBoundLogger

from . import Handler
from ..model.health import HealthSchema, ReadinessSchema, LivenessSchema
from ..services.health import HealthService


class HealthHandler(Handler):
    """
    Health resource
    """
    _log: FilteringBoundLogger
    _health_service: HealthService

    def __init__(self, health_service: HealthService):
        Handler.__init__(self, {'Health': HealthSchema()})
        self._health_service = health_service

    def on_get(self, _: Request, res: Response):
        """Handles health GET requests.
        ---
        description: Get the health status
        responses:
            200:
                description: 'OK'
                schema:
                    $ref: '#/definitions/Health'
            503:
                description: 'Service Unavailable'
                schema:
                    $ref: '#/definitions/Health'
        """
        try:
            if self._check_health_probe():
                self._log.debug('check ok')
                res.status = HTTP_200
                res.text = HealthSchema().dumps({'alive': True})
            else:
                self._log.debug('check ko')
                res.status = HTTP_503
                res.text = HealthSchema().dumps({'alive': False})
        except Exception as err:
            res.text, res.status = self.handle_generic_error(err)

    def on_delete(self, _: Request, res: Response):
        """Handles health DELETE requests.
        ---
        description: Stop the health service
        responses:
            204:
                description: 'NO CONTENT'
        """
        try:
            self._health_service.interrupt = True
            res.status = HTTP_204
        except Exception as err:
            res.text, res.status = self.handle_generic_error(err)

    def _check_health_probe(self) -> bool:
        readiness_probes = self._health_service.get_readiness_checks()
        liveness_probes = self._health_service.get_liveness_checks()
        is_rdy = readiness_probes['status'] == HTTP_200
        is_live = liveness_probes['status'] == HTTP_200
        return is_rdy and is_live


class ReadinessHandler(Handler):
    """
    Readiness resource
    """
    _log: FilteringBoundLogger
    _health_service: HealthService

    def __init__(self, health_service: HealthService):
        Handler.__init__(self, {'Readiness': ReadinessSchema()})
        self._health_service = health_service

    def on_get(self, _: Request, res: Response):
        """Handles health readiness GET requests.
        ---
        description: Get the health readiness probes
        responses:
            200:
                description: 'OK'
                schema:
                    $ref: '#/definitions/Readiness'
            503:
                description: 'Service Unavailable'
                schema:
                    $ref: '#/definitions/Readiness'
        """
        try:
            readiness_probes = self._health_service.get_readiness_checks()
            res.status = readiness_probes.pop('status')
            res.text = ReadinessSchema().dumps(readiness_probes)
        except Exception as err:
            res.text, res.status = self.handle_generic_error(err)


class LivenessHandler(Handler):
    """
    Liveness resource
    """
    _log: FilteringBoundLogger
    _health_service: HealthService

    def __init__(self, health_service: HealthService):
        Handler.__init__(self, {'Liveness': LivenessSchema()})
        self._health_service = health_service

    def on_get(self, _: Request, res: Response):
        """Handles health liveness GET requests.
        ---
        description: Get the health liveness probes
        responses:
            200:
                description: 'OK'
                schema:
                    $ref: '#/definitions/Liveness'
            503:
                description: 'Service Unavailable'
                schema:
                    $ref: '#/definitions/Liveness'
        """
        try:
            liveness_probes = self._health_service.get_liveness_checks()
            res.status = liveness_probes.pop('status')
            res.text = LivenessSchema().dumps(liveness_probes)
        except Exception as err:
            res.text, res.status = self.handle_generic_error(err)
