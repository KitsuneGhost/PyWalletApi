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
    def create(data: dict):
        """Generic create method — internal helper."""

        transaction = Transaction(**data)
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def deposit(user_id: int, wallet_id: int, amount):
        """Create a deposit transaction."""

        transaction = Transaction(
            type=TransactionType.DEPOSIT,
            amount=amount,
            user_id=user_id,
            to_wallet_id=wallet_id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def withdraw(user_id: int, wallet_id: int, amount):
        """Create a withdrawal transaction."""

        transaction = Transaction(
            type=TransactionType.WITHDRAW,
            amount=amount,
            user_id=user_id,
            from_wallet_id=wallet_id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction

    @staticmethod
    def transfer(user_id: int, from_wallet_id: int, to_wallet_id: int, amount):
        """Create a transfer transaction."""

        transaction = Transaction(
            type=TransactionType.TRANSFER,
            amount=amount,
            user_id=user_id,
            from_wallet_id=from_wallet_id,
            to_wallet_id=to_wallet_id
        )
        db.session.add(transaction)
        db.session.commit()
        return transaction
