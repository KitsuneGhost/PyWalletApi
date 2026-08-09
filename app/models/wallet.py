from datetime import datetime
from app.extensions.extensions import db


class Wallet(db.Model):
    """
    A class representing a user's wallet.
    """

    __tablename__ = "wallets"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0.00, nullable=False)
    currency = db.Column(db.String(3), default="EUR", nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    active = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Foreign key to User
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    __table_args__ = (
        db.CheckConstraint("balance >= 0", name="ck_wallet_balance_nonnegative"),
        db.UniqueConstraint("user_id", "name", name="uq_wallet_user_name"),
    )

    # Relationships
    owner = db.relationship("User", back_populates="wallets")

    outgoing_transactions = db.relationship(
        "Transaction",
        foreign_keys="Transaction.from_wallet_id",
        back_populates="from_wallet",
        lazy="selectin"
    )
    incoming_transactions = db.relationship(
        "Transaction",
        foreign_keys="Transaction.to_wallet_id",
        back_populates="to_wallet",
        lazy="selectin"
    )
