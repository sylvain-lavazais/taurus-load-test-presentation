import falcon

from mirror_reader.handler.handler import Handler
from mirror_reader.model.health import HealthSchema, ReadinessSchema, LivenessSchema


class HealthHandler(Handler):
    """
    Health resource
    """

    def __init__(self, health_service):
        Handler.__init__(self, {'Health': HealthSchema()})
        self.health_service = health_service

    def on_get(self, _, res):
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
                res.status = falcon.HTTP_200
                res.body = HealthSchema().dumps({'alive': True}).data
            else:
                res.status = falcon.HTTP_503
                res.body = HealthSchema().dumps({'alive': False}).data
        except Exception as err:
            res.body, res.status = self.handle_generic_error(err)

    def _check_health_probe(self) -> bool:
        readiness_probes = self.health_service.get_readiness_checks()
        liveness_probes = self.health_service.get_liveness_checks()
        is_rdy = readiness_probes['status'] == falcon.HTTP_200
        is_live = liveness_probes['status'] == falcon.HTTP_200
        return is_rdy and is_live


class ReadinessHandler(Handler):
    """
    Readiness resource
    """

    def __init__(self, health_service):
        Handler.__init__(self, {'Readiness': ReadinessSchema()})
        self.health_service = health_service

    def on_get(self, _, res):
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
            readiness_probes = self.health_service.get_readiness_checks()
            res.status = readiness_probes.pop('status')
            res.body = ReadinessSchema().dumps(readiness_probes).data
        except Exception as err:
            res.body, res.status = self.handle_generic_error(err)


class LivenessHandler(Handler):
    """
    Liveness resource
    """

    def __init__(self, health_service):
        Handler.__init__(self, {'Liveness': LivenessSchema()})
        self.health_service = health_service

    def on_get(self, _, res):
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
            liveness_probes = self.health_service.get_liveness_checks()
            res.status = liveness_probes.pop('status')
            res.body = LivenessSchema().dumps(liveness_probes).data
        except Exception as err:
            res.body, res.status = self.handle_generic_error(err)
