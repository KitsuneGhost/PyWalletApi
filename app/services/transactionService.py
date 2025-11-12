from sqlalchemy.exc import IntegrityError

from app.repositories.transactionRepository import TransactionRepository
from app.models.transaction import Transaction, TransactionType
from app.extensions.extensions import db
from app.repositories.userRepository import UserRepository
from app.repositories.walletRepository import WalletRepository


class TransactionService:

    @staticmethod
    def get_all():
        """Return all transactions."""

        return TransactionRepository.get_all()

    @staticmethod
    def get_by_id(transaction_id):
        transaction = TransactionRepository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError("This transaction does not exist")
        return transaction

    @staticmethod
    def get_by_user(user_id):
        transactions = TransactionRepository.get_by_user(user_id)
        if not transactions:
            raise ValueError("This user does not exist")
        return transactions

    @staticmethod
    def create(data):

        if not UserRepository.get_by_id(data["user_id"]):
            raise ValueError("This user does not exist")
        if not WalletRepository.get_by_id(data["to_wallet_id"]):
            raise ValueError("This wallet does not exist")
        if not WalletRepository.get_by_id(data["from_wallet_id"]):
            raise ValueError("This wallet does not exist")

        new_transaction = Transaction(
            user_id=data["user_id"],
            to_wallet_id=data["to_wallet_id"],
            from_wallet_id=data["from_wallet_id"],
            type=data["type"])

        try:
            TransactionRepository.create(new_transaction)
            return new_transaction
        except IntegrityError as e:
            raise ValueError("User with this email or username already exists") from e
