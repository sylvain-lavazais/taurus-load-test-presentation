from falcon import Request, Response, HTTP_200, HTTP_404
from structlog.typing import FilteringBoundLogger

from . import Handler
from ..models.message import MessageSchema
from ..services.message import MessageService


class MessageKeyHandler(Handler):
    """
    Message resource
    """
    _log: FilteringBoundLogger
    _svc: MessageService

    def __init__(self, message_service: MessageService):
        Handler.__init__(self, {'Message': MessageSchema()})
        self._svc = message_service

    def on_get(self, req: Request, res: Response, key: str):
        """ Handles messages get requests.
        ---
        summary: 'Retrieve a message'
        description: 'Retrieve a bulk of messages by code keys and source type'
        produces: ['application/json']
        parameters:
            - in: path
              description: the key of message to retrieve
              required: true
        responses:
            200:
                description: 'Message found'
                schema:
                    $ref: '#/definitions/MessageReport'
            400:
                description: 'Bad Request'
                schema:
                    $ref: '#/definitions/ErrorsPayload'
            404:
                description: 'No message found'
                schema:
                    $ref: '#/definitions/MessageReport'
            413:
                description: 'Too Many Messages'
                schema:
                    $ref: '#/definitions/ErrorsPayload'
            500:
                description: 'Internal Server Error'
                schema:
                    $ref: '#/definitions/ErrorsPayload'
        """
        try:
            data, err = self._svc.read(key)

            if len(err) > 0:
                res.status = HTTP_404
                res.text = MessageSchema().dumps({'errors': err})
            else:
                res.status = HTTP_200
                res.text = MessageSchema().dumps({'data': data})

        except Exception as exc:
            res.text, res.status = self.handle_generic_error(exc)

    def on_patch(self, req: Request, res: Response):
        pass

    def on_put(self, req: Request, res: Response):
        pass

    def on_delete(self, req: Request, res: Response):
        pass
