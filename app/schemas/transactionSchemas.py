from app.extensions.extensions import ma
from marshmallow import fields, validate


class DepositSchema(ma.Schema):
    """Schema for validating deposit transaction creation input (deserialization)"""

    amount = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01, error="Amount must be positive")
    )


class WithdrawSchema(ma.Schema):
    """Schema for validating withdraw transaction creation input (deserialization)"""

    amount = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01, error="Amount must be positive")
    )


class TransferSchema(ma.Schema):
    """Schema for validating transfer transaction creation input (deserialization)"""

    to_wallet_id = fields.Int(required=True)
    amount = fields.Decimal(
        required=True,
        places=2,
        validate=validate.Range(min=0.01)
    )

class TransactionResponseSchema(ma.Schema):
    """Schema for serializing transaction data in responses"""

    id = fields.Int(dump_only=True)
    type = fields.Function(lambda transaction: transaction.type.value, dump_only=True)
    amount = fields.Decimal(as_string=True)
    timestamp = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)
    from_wallet_id = fields.Int(allow_none=True, dump_only=True)
    to_wallet_id = fields.Int(allow_none=True, dump_only=True)
