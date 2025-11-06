from app.app import ma
from marshmallow import fields


class UserResponseSchema(ma.Schema):
    """Schema for serializing user data in responses"""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Email()
    role = fields.Str()
    created_at = fields.DateTime()