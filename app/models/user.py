from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions.extensions import db


class User(db.Model):
    """
    A class representing user model.
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='USER')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Bidirectional, safe defaults
    wallets = db.relationship(
        'Wallet',
        back_populates='owner',
        lazy='selectin',  # efficient batch loading
        cascade='all, delete-orphan'  # delete child rows when user is deleted
    )
    transactions = db.relationship(
        'Transaction',
        back_populates='user',
        lazy='selectin',
        cascade='all, delete-orphan'
    )

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

# for launching (SQLAlchemy doest recognize them unless imported anywhere)

from app.models.wallet import Wallet
from app.models.transaction import Transaction