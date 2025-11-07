from app.app import ma
from marshmallow import fields, validate


class WalletUpdateSchema(ma.Schema):
    """Schema for validating wallet update input (deserialization).
    Does not support currency migrations"""

    name = fields.Str(
        validate=[
            validate.Length(min=3, max=20),
            validate.Regexp(r'^\S(.*\S)?$', error="Name cannot be blank or contain only spaces.")])

    balance = fields.Decimal(
        as_string=True,
        places=2,
        validate=validate.Range(min=0, error="Balance can't be negative"))
