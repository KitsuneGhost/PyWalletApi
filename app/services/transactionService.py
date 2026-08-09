from decimal import Decimal

from app.extensions.extensions import db
from app.models.transaction import Transaction, TransactionType
from app.models.wallet import Wallet


class TransactionService:
    @staticmethod
    def _wallet(wallet_id):
        return db.session.execute(
            db.select(Wallet).where(Wallet.id == wallet_id).with_for_update()
        ).scalar_one_or_none()

    @staticmethod
    def _amount(value):
        amount = Decimal(value).quantize(Decimal("0.01"))
        if amount <= 0 or amount > Decimal("9999999999.99"):
            raise ValueError("Invalid amount")
        return amount

    @classmethod
    def withdraw(cls, user_id, wallet_id, amount):
        amount = cls._amount(amount)
        try:
            wallet = cls._wallet(wallet_id)
            if not wallet or not wallet.active or wallet.user_id != user_id:
                raise ValueError("Wallet not found")
            if wallet.balance < amount:
                raise ValueError("Insufficient funds")
            wallet.balance -= amount
            tx = Transaction(type=TransactionType.WITHDRAW, amount=amount, user_id=user_id, from_wallet_id=wallet.id)
            db.session.add(tx)
            db.session.commit()
            return tx
        except Exception:
            db.session.rollback()
            raise

    @classmethod
    def transfer(cls, user_id, from_id, to_wallet_id, amount):
        to_id = to_wallet_id
        if from_id == to_id:
            raise ValueError("Cannot transfer to the same wallet")
        amount = cls._amount(amount)
        try:
            # Stable lock ordering avoids deadlocks on databases with row locks.
            wallets = {wid: cls._wallet(wid) for wid in sorted((from_id, to_id))}
            source, target = wallets[from_id], wallets[to_id]
            if not source or not source.active or source.user_id != user_id:
                raise ValueError("Source wallet not found")
            if not target or not target.active:
                raise ValueError("Destination wallet not found")
            if source.currency != target.currency:
                raise ValueError("Currency conversion is not supported")
            if source.balance < amount:
                raise ValueError("Insufficient funds")
            if target.balance + amount > Decimal("9999999999.99"):
                raise ValueError("Balance limit exceeded")
            source.balance -= amount
            target.balance += amount
            tx = Transaction(type=TransactionType.TRANSFER, amount=amount, user_id=user_id, from_wallet_id=source.id, to_wallet_id=target.id)
            db.session.add(tx)
            db.session.commit()
            return tx
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_for_user(user_id, page=1, per_page=20):
        return db.paginate(
            db.select(Transaction)
            .where(Transaction.user_id == user_id)
            .order_by(Transaction.timestamp.desc(), Transaction.id.desc()),
            page=page,
            per_page=per_page,
            error_out=False,
        )
