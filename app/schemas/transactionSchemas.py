from app.app import ma
from marshmallow import fields, validate, validates_schema, ValidationError


class DepositSchema(ma.Schema):
    """Schema for validating deposit transaction creation input (deserialization)"""

    wallet_id = fields.Int(required=True)
    amount = fields.Decimal(
        required=True,
        validate=validate.Range(min=0.01, error="Amount must be positive")
    )


class WithdrawSchema(ma.Schema):
    """Schema for validating withdraw transaction creation input (deserialization)"""

    wallet_id = fields.Int(required=True)
    amount = fields.Decimal(
        required=True,
        validate=validate.Range(min=0.01, error="Amount must be positive")
    )


class TransferSchema(ma.Schema):
    """Schema for validating transfer transaction creation input (deserialization)"""

    from_wallet_id = fields.Int(required=True)
    to_wallet_id = fields.Int(required=True)
    amount = fields.Decimal(
        required=True,
        validate=validate.Range(min=0.01)
    )

    @validates_schema
    def validate_wallets(self, data, **kwargs):
        if data["from_wallet_id"] == data["to_wallet_id"]:
            raise ValidationError("Cannot transfer to the same wallet")


class TransactionResponseSchema(ma.Schema):
    """Schema for serializing transaction data in responses"""

    id = fields.Int(dump_only=True)
    type = fields.Str(dump_only=True)
    amount = fields.Decimal(as_string=True)
    timestamp = fields.DateTime(dump_only=True)
    user_id = fields.Int(dump_only=True)
    from_wallet_id = fields.Int(allow_none=True, dump_only=True)
    to_wallet_id = fields.Int(allow_none=True, dump_only=True)
