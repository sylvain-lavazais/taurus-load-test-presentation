import threading
from typing import Any
from uuid import uuid4

import falcon
import structlog


class TrackingId:
    # local thread
    _local_thread = threading.local()

    def __init__(self):
        self._logger = structlog.get_logger('falcon')

        self._excluded_resources = (
                '/_health',
                '/_private/_liveness',
                '/_private/_readiness',
                '/_private/_metrics',
        )

    def get_request_id(self) -> str | None:
        if hasattr(self._local_thread, "tracking_id"):
            return self._local_thread.tracking_id
        return None

    def set_request_id(self, tracking_id: str = None) -> None:
        self._local_thread.tracking_id = tracking_id

    def process_request(self, req: falcon.Request, _: falcon.Response) -> None:
        """
        Provide a request id for tying together all log entries made during
        request processing. If the client provided an x-request-id, use that,
        otherwise generate one.
        """
        self.set_request_id(req.get_header('x-request-id', default=str(uuid4())))

    def process_response(self, _: falcon.Request, __: falcon.Response, ___, ____: bool) -> None:
        """
        Remove x-request-id from thread local storage in preparation for the next request
        """

        self.set_request_id()
