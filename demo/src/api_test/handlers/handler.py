from types import TracebackType

import structlog
from falcon import HTTP_500
from structlog.typing import FilteringBoundLogger

from ..model.errors import GenericErrorPayloadSchema


class Handler:
    """
    Generic resource class.
    """
    _log: FilteringBoundLogger
    _schemas: dict

    def __init__(self, schemas: dict = None):
        self._schemas = schemas
        self._log = structlog.get_logger()

    def handle_generic_error(self, err: Exception) -> (any, str):
        error = dict()
        error['message'] = str(err)
        error['error_status'] = HTTP_500
        self._log.exception('generic error handling')
        return GenericErrorPayloadSchema().dumps(error), HTTP_500
