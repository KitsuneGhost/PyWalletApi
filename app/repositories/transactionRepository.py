from app.models.transaction import Transaction, TransactionType
from app.extensions.extensions import db


class TransactionRepository:
    """Handles database operations for Transaction model.
    Transactions are IMMUTABLE, therefore the is no update/delete methods"""

    @staticmethod
    def get_all():
        """Return all transactions."""

        return Transaction.query.all()

    @staticmethod
    def get_by_id(transaction_id: int):
        """Return a single transaction by ID."""

        return Transaction.query.get(transaction_id)

    @staticmethod
    def get_by_user(user_id: int):
        """Return all transactions made by a specific user."""

        return Transaction.query.filter_by(user_id=user_id).all()

    @staticmethod
    def create(transaction: Transaction):
        """Generic create method — internal helper."""

        db.session.add(transaction)
        db.session.commit()
        return transaction
