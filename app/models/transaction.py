from datetime import datetime
from enum import Enum
from app.extensions.extensions import db


class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"


class Transaction(db.Model):
    """
    A class representing a financial transaction.
    """

    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    from_wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=True)
    to_wallet_id = db.Column(db.Integer, db.ForeignKey("wallets.id"), nullable=True)

    # Relationships
    user = db.relationship("User", back_populates="transactions")
    from_wallet = db.relationship(
        "Wallet",
        foreign_keys=[from_wallet_id],
        back_populates="outgoing_transactions"
    )
    to_wallet = db.relationship(
        "Wallet",
        foreign_keys=[to_wallet_id],
        back_populates="incoming_transactions"
    )
