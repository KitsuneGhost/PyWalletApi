from app.extensions.extensions import db
from app.models.wallet import Wallet
from sqlalchemy import and_


class WalletRepository:

    @staticmethod
    def get_all():
        """Returns a list of all wallets"""

        return Wallet.query.all()

    @staticmethod
    def get_by_id(wallet_id: int):
        """Returns a wallet with a specific id"""

        return Wallet.query.get(wallet_id)

    @staticmethod
    def filter_wallets(
            user_id=None,
            name=None,
            currency=None,
            min_balance=None,
            max_balance=None,
            min_date=None,
            max_date=None,
            sort_by="created_at",
            order="desc",
            page=1,
            per_page=10,
    ):
        """Filters and paginates wallets"""

        query = Wallet.query
        filters = []

        # conditional query
        if user_id is not None:
            filters.append(Wallet.user_id == user_id)
        if name is not None:
            filters.append(Wallet.name == name)
        if currency is not None:
            filters.append(Wallet.currency == currency)
        if min_balance is not None:
            filters.append(Wallet.balance >= min_balance)
        if max_balance is not None:
            filters.append(Wallet.balance <= max_balance)
        if min_date is not None:
            filters.append(Wallet.created_at >= min_date)
        if max_date is not None:
            filters.append(Wallet.created_at <= max_date)

        if filters:
            query = query.filter(and_(*filters))

        # Sorting
        sort_column = getattr(Wallet, sort_by, Wallet.created_at)
        query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated

    @staticmethod
    def create(wallet: Wallet):
        """Creates a new wallet"""

        try:
            db.session.add(wallet)
            db.session.commit()
            return wallet
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete(wallet: Wallet):
        """Deletes a wallet"""

        try:
            db.session.delete(wallet)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update(wallet: Wallet, data: dict):
        """Updates a wallet"""

        try:
            # Update only the fields that exist in the model
            for field, value in data.items():
                if hasattr(Wallet, field):  # check that field belongs to User model
                    setattr(wallet, field, value)
            db.session.commit()
            return wallet
        except Exception as e:
            db.session.rollback()
            raise e
