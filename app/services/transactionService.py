from app.repositories.transactionRepository import TransactionRepository
from app.models.transaction import Transaction, TransactionType
from app.extensions.extensions import db


class TransactionService:

    @staticmethod
    def get_all():
        """Return all transactions."""

        return TransactionRepository.get_all()

    @staticmethod
    def get_by_id(transaction_id):

        return TransactionRepository.get_by_id(transaction_id)

    @staticmethod
    def get_by_user(user_id):

        return TransactionRepository.get_by_user(user_id)

    @staticmethod
    def create(transaction):
        pass
