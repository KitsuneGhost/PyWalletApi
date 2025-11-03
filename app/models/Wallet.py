from datetime import datetime
from app.db.db import db


class Wallet(db.Model):
    __tablename__ = 'wallets'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    balance = db.Column(db.Numeric(12, 2), default=0.00)
    currency = db.Column(db.String(10), default='EUR')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    outgoing_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.from_wallet_id',
        backref='from_wallet',
        lazy=True
    )
    incoming_transactions = db.relationship(
        'Transaction',
        foreign_keys='Transaction.to_wallet_id',
        backref='to_wallet',
        lazy=True
    )
