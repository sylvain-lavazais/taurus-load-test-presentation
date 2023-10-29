from marshmallow import Schema, fields


class ErrorsPayloadSchema(Schema):
    errors = fields.List(fields.String(), required=True)


class GenericErrorPayloadSchema(Schema):
    message = fields.String()
    error_status = fields.String()
