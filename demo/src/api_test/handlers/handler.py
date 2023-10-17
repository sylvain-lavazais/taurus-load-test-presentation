import falcon
import structlog

from mirror_reader.model.errors import GenericErrorPayloadSchema


class Handler:
    """
    Generic resource class.
    """

    def __init__(self, schemas=None):
        self.schemas = schemas
        self._logger = structlog.get_logger()

    def handle_generic_error(self, err) -> (any, str):
        error = dict()
        error['message'] = str(err)
        error['error_status'] = falcon.HTTP_500
        self._logger.error(err)
        return GenericErrorPayloadSchema().dumps(error).data, falcon.HTTP_500
