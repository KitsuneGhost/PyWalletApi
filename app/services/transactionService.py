from sqlalchemy.exc import IntegrityError

from app.repositories.transactionRepository import TransactionRepository
from app.models.transaction import Transaction
from app.repositories.userRepository import UserRepository
from app.repositories.walletRepository import WalletRepository


class TransactionService:

    def __init__(
            self,
            transaction_repository: TransactionRepository,
            user_repository: UserRepository,
            wallet_repository: WalletRepository
    ):
        self.transaction_repository = transaction_repository
        self.user_repository = user_repository
        self.wallet_repository = wallet_repository

    def get_all(self) -> list[Transaction]:
        """Return all transactions."""

        return self.transaction_repository.get_all()

    def get_by_id(self, transaction_id: int) -> Transaction | None:
        transaction = self.transaction_repository.get_by_id(transaction_id)
        if not transaction:
            raise ValueError("This transaction does not exist")
        return transaction

    def get_by_user(self, user_id: int) -> Transaction | None:
        transactions = self.transaction_repository.get_by_user(user_id)
        if not transactions:
            raise ValueError("This user does not exist")
        return transactions

    def create(self, data) -> Transaction:

        if not self.user_repository.get_by_id(data["user_id"]):
            raise ValueError("This user does not exist")
        if not self.wallet_repository.get_by_id(data["to_wallet_id"]):
            raise ValueError("This wallet does not exist")
        if not self.wallet_repository.get_by_id(data["from_wallet_id"]):
            raise ValueError("This wallet does not exist")

        new_transaction = Transaction(
            user_id=data["user_id"],
            to_wallet_id=data["to_wallet_id"],
            from_wallet_id=data["from_wallet_id"],
            type=data["type"])

        try:
            self.transaction_repository.create(new_transaction)
            return new_transaction
        except IntegrityError as e:
            raise ValueError("User with this email or username already exists") from e
