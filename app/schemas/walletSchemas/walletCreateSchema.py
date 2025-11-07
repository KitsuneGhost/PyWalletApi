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