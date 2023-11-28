from typing import Dict

from marshmallow import Schema, fields


class MessageDataSchema(Schema):
    key: str = fields.Str(required=True)
    attributes: dict = fields.Dict(keys=fields.Str(), required=True)


class MessageErrorSchema(Schema):
    error_code: Dict[str, str] = fields.Dict(keys=fields.Str(), values=fields.Str(), required=True)
    error: str = fields.Str(required=True)


class MessageSchema(Schema):
    data: MessageDataSchema = fields.Nested(MessageDataSchema(), many=True)
    errors: MessageErrorSchema = fields.Nested(MessageErrorSchema(), many=True)
