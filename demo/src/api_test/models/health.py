from marshmallow import Schema, fields


class HealthSchema(Schema):
    alive = fields.Bool(required=True)


class ReadinessSchema(Schema):
    dns_lookup = fields.Str(required=True)
    postgres = fields.Str(required=True)


class LivenessSchema(Schema):
    memory = fields.Str(required=True)
    cpu = fields.Str(required=True)
    postgres_pool = fields.Str(required=True)
