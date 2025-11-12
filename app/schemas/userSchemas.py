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


class UserResponseSchema(ma.Schema):
    """Schema for serializing user data in responses"""

    id = fields.Int(dump_only=True)
    username = fields.Str(dump_only=True)
    email = fields.Email(dump_only=True)
    role = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


class UserUpdateSchema(ma.Schema):
    """Schema for validating user update input (deserialization)"""

    username = fields.Str(validate=validate.Length(min=5, max=80))

    email = fields.Email()

    password = fields.Str(
        load_only=True,
        validate=validate.Length(min=8, max=32))

    role = fields.Str(validate=validate.OneOf(["USER", "ADMIN"]))
