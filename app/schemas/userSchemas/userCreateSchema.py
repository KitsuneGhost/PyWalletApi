from app.app import ma
from marshmallow import fields, validate


class UserCreateSchema(ma.Schema):
    """Schema for validating user creation input (deserialization)"""

    username = fields.Str(
        required=True,
        validate=validate.Length(min=5, max=80))

    email = fields.Email(required=True)

    password = fields.Str(
        required=True,
        load_only=True,
        validate=validate.Length(min=8, max=32))

    role = fields.Str(
        validate=validate.OneOf(["USER", "ADMIN"]),
        load_default="USER")
