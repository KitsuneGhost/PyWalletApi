from datetime import datetime
from app.db.db import db
from enum import Enum


class TransactionType(Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAW = "WITHDRAW"
    TRANSFER = "TRANSFER"


class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.Enum(TransactionType), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    from_wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=True)
    to_wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=True)
