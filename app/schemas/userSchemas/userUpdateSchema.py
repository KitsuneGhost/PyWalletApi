from app.app import ma
from marshmallow import fields, validate


class UserUpdateSchema(ma.Schema):
    """Schema for validating user update input (deserialization)"""

    username = fields.Str(validate=validate.Length(min=5, max=80))

    email = fields.Email()

    password = fields.Str(
        load_only=True,
        validate=validate.Length(min=8, max=32))

    role = fields.Str(validate=validate.OneOf(["USER", "ADMIN"]))