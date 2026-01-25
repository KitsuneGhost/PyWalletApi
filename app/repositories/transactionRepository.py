from app.models.transaction import Transaction, TransactionType
from app.extensions.extensions import db


class TransactionRepository:
    """Handles database operations for Transaction model.
    Transactions are IMMUTABLE, therefore the is no update/delete methods"""

    def __init__(self, model: type[Transaction]):
        self.model = model

    def get_all(self) -> list[Transaction]:
        """Return all transactions."""

        return self.model.query.all()

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        """Return a single transaction by ID."""

        return self.model.query.get(transaction_id)

    def get_by_user(self, user_id: int) -> Transaction | None:
        """Return all transactions made by a specific user."""

        return self.model.query.filter_by(user_id=user_id).all()

    def create(self, transaction: Transaction) -> Transaction:
        """Generic create method — internal helper."""

        db.session.add(transaction)
        db.session.commit()
        return transaction
