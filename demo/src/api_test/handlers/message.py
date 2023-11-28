from . import Handler
from ..services.message import MessageService


class Message(Handler):
    """
    Message resource
    """

    def __init__(self, message_service: MessageService):
        pass
