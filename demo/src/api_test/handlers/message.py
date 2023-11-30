from falcon import Request, Response, HTTP_200, HTTP_404, HTTP_204, HTTP_400, HTTP_409, HTTP_500, HTTP_201
from falcon.errors import MediaMalformedError
from structlog.typing import FilteringBoundLogger

from . import Handler
from ..models.message import MessageSchema
from ..services.message import MessageService, ENTITY_ALREADY_EXIST


class MessageKeyHandler(Handler):
    """
    Message resource
    """
    _log: FilteringBoundLogger
    _svc: MessageService

    def __init__(self, message_service: MessageService):
        Handler.__init__(self, {'Message': MessageSchema()})
        self._svc = message_service

    def on_get(self, _: Request, res: Response, key: str):
        """ Handles messages get requests.
        ---
        summary: 'Retrieve a message'
        description: 'Retrieve a message by code its key'
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
            404:
                description: 'No message found'
                schema:
                    $ref: '#/definitions/MessageReport'
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

    def on_put(self, req: Request, res: Response, key: str):
        """ Handles messages PUT requests.
        ---
        summary: 'Update a message'
        description: 'Update a message by code its key'
        produces: ['application/json']
        parameters:
            - in: path
              description: the key of message to update
              required: true
        responses:
            204:
                description: 'Message updated with success'
            400:
                description: 'Bad Request'
                schema:
                    $ref: '#/definitions/MessageReport'
            404:
                description: 'No message found'
                schema:
                    $ref: '#/definitions/MessageReport'
            500:
                description: 'Internal Server Error'
                schema:
                    $ref: '#/definitions/ErrorsPayload'
        """

        try:
            # noinspection PyArgumentList
            body = req.get_media(default_when_empty=dict())

            if 'data' not in body:
                res.status = HTTP_400
                res.text = MessageSchema().dumps(
                        {'errors': [{'error_code': {'HTTP_400': 'bad request'},
                                     'error'     : '`data` field is absent'}]}
                )
            else:
                data = body['data']

                if 'key' not in data or 'attributes' not in data:
                    res.status = HTTP_400
                    res.text = MessageSchema().dumps(
                            {'errors': [{'error_code': {'HTTP_400': 'bad request'},
                                         'error'     : '`key` and/or `attributes` field(s) is(are) absent(s)'}]}
                    )
                else:
                    err = self._svc.update(data['attributes'], key)

                    if len(err) > 0:
                        res.status = HTTP_404
                        res.text = MessageSchema().dumps({'errors': err})
                    else:
                        res.status = HTTP_204

        except MediaMalformedError as json_err:
            res.status = json_err.status
            res.text = MessageSchema().dumps(
                    {'errors': [{'error_code': {'HTTP_400': 'bad request'},
                                 'error'     : json_err.description}]}
            )
        except Exception as exc:
            res.text, res.status = self.handle_generic_error(exc)

    def on_delete(self, _: Request, res: Response, key: str):
        """ Handles messages DELETE requests.
        ---
        summary: 'Delete a message'
        description: 'Delete a message by code its key'
        produces: ['application/json']
        parameters:
            - in: path
              description: the key of message to delete
              required: true
        responses:
            204:
                description: 'Message deleted'
            404:
                description: 'No message found'
                schema:
                    $ref: '#/definitions/MessageReport'
            500:
                description: 'Internal Server Error'
                schema:
                    $ref: '#/definitions/ErrorsPayload'
        """
        try:
            err = self._svc.delete(key)

            if len(err) > 0:
                res.status = HTTP_404
                res.text = MessageSchema().dumps({'errors': err})
            else:
                res.status = HTTP_204

        except Exception as exc:
            res.text, res.status = self.handle_generic_error(exc)


class MessageHandler(Handler):
    """
    Message resource
    """
    _log: FilteringBoundLogger
    _svc: MessageService

    def __init__(self, message_service: MessageService):
        Handler.__init__(self, {'Message': MessageSchema()})
        self._svc = message_service

    def on_post(self, req: Request, res: Response):
        """ Handles message POST requests.
        ---
        summary: 'Create a new message'
        description: 'Create a new message'
        produces: ['application/json']
        responses:
            201:
                description: 'Message updated with success'
            400:
                description: 'Bad Request'
                schema:
                    $ref: '#/definitions/MessageReport'
            409:
                description: 'Message already exist'
                schema:
                    $ref: '#/definitions/MessageReport'
            500:
                description: 'Internal Server Error'
                schema:
                    $ref: '#/definitions/ErrorsPayload'
        """

        try:
            # noinspection PyArgumentList
            body = req.get_media(default_when_empty=dict())

            if 'data' not in body:
                res.status = HTTP_400
                res.text = MessageSchema().dumps(
                        {'errors': [{'error_code': {'HTTP_400': 'bad request'},
                                     'error'     : '`data` field is absent'}]}
                )
            else:
                data = body['data']

                if 'key' not in data or 'attributes' not in data:
                    res.status = HTTP_400
                    res.text = MessageSchema().dumps(
                            {'errors': [{'error_code': {'HTTP_400': 'bad request'},
                                         'error'     : '`key` and/or `attributes` field(s) is(are) absent(s)'}]}
                    )
                else:
                    err = self._svc.create(data['attributes'], data['key'])

                    if len(err) > 0:
                        if err[0]['error_code']['CREATE'] is ENTITY_ALREADY_EXIST:
                            res.status = HTTP_409
                            res.text = MessageSchema().dumps({'errors': err})
                        else:
                            res.status = HTTP_500
                            res.text = MessageSchema().dumps({'errors': err})
                    else:
                        res.status = HTTP_201
                        # TODO : return the created entity at the end

        except MediaMalformedError as json_err:
            res.status = json_err.status
            res.text = MessageSchema().dumps(
                    {'errors': [{'error_code': {'HTTP_400': 'bad request'},
                                 'error'     : json_err.description}]}
            )
        except Exception as exc:
            res.text, res.status = self.handle_generic_error(exc)
