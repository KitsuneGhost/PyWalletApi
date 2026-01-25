from app.extensions.extensions import db
from app.models.wallet import Wallet
from sqlalchemy import and_


class WalletRepository:

    def __init__(self, model: type[Wallet]):
        self.model = model

    def get_all(self) -> Wallet | None:
        """Returns a list of all wallets"""

        return self.model.query.all()

    def get_by_id(self, wallet_id: int) -> Wallet | None:
        """Returns a wallet with a specific id"""

        return self.model.query.get(wallet_id)

    def filter_wallets(
            self,
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

        query = self.model.query
        filters = []

        # conditional query
        if user_id is not None:
            filters.append(self.model.user_id == user_id)
        if name is not None:
            filters.append(self.model.name == name)
        if currency is not None:
            filters.append(self.model.currency == currency)
        if min_balance is not None:
            filters.append(self.model.balance >= min_balance)
        if max_balance is not None:
            filters.append(self.model.balance <= max_balance)
        if min_date is not None:
            filters.append(self.model.created_at >= min_date)
        if max_date is not None:
            filters.append(self.model.created_at <= max_date)

        if filters:
            query = query.filter(and_(*filters))

        # Sorting
        sort_column = getattr(self.model, sort_by, self.model.created_at)
        query = query.order_by(sort_column.desc() if order == "desc" else sort_column.asc())

        # Pagination
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)
        return paginated


    def create(self, wallet: Wallet) -> Wallet:
        """Creates a new wallet"""

        try:
            db.session.add(wallet)
            db.session.commit()
            return wallet
        except Exception as e:
            db.session.rollback()
            raise e


    def delete(self, wallet: Wallet) -> None:
        """Deletes a wallet"""

        try:
            db.session.delete(wallet)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, wallet: Wallet, data: dict) -> Wallet | None:
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
