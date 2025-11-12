from decimal import Decimal

from app.app import ma
from marshmallow import fields, validate, pre_load


class WalletCreateSchema(ma.Schema):
    """Schema for validating wallet creation input (deserialization)."""

    @pre_load
    def normalize_currency(self, data, **kwargs):
        """Forces currency to uppercase e.g. usd -> USD"""

        if "currency" in data and isinstance(data["currency"], str):
            data["currency"] = data["currency"].upper()
        return data

    name = fields.Str(
        required=True,
        validate=[
            validate.Length(min=3, max=20),
            validate.Regexp(r'^\S(.*\S)?$', error="Name cannot be blank or contain only spaces.")])

    balance = fields.Decimal(
        as_string=True,
        load_default=Decimal("0.00"),
        validate=validate.Range(min=0, error="Balance can't be negative"))

    currency = fields.Str(
        validate=validate.OneOf(["EUR", "USD", "CHF", "RUB"]),
        load_default="EUR")

    user_id = fields.Int(required=True)


class WalletResponseSchema(ma.Schema):
    """Schema for serializing wallet data in responses"""

    id = fields.Int(dump_only=True)

    name = fields.Str(dump_only=True)

    balance = fields.Decimal(
        as_string=True,     # ensures JSON-safe serialization
        places=2,           # match db.Numeric(12, 2) precision
        dump_only=True
    )
    currency = fields.Str(dump_only=True)

    user_id = fields.Int(dump_only=True)


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
