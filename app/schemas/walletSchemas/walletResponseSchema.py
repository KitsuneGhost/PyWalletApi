from app.app import ma
from marshmallow import fields


class WalletResponseSchema(ma.Schema):
    """Schema for serializing wallet data in responses"""

    id = fields.Int(dump_only=True)

    name = fields.Str()

    balance = fields.Decimal(
        as_string=True,  # ensures JSON-safe serialization
        places=2  # match db.Numeric(12, 2) precision
    )
    currency = fields.Str()

    user_id = fields.Int(dump_only=True)
