from app.models.wallet import Wallet
from app.repositories.userRepository import UserRepository
from app.repositories.walletRepository import WalletRepository


class WalletService:

    def __init__(self, repository: WalletRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository

    def get_all(self) -> list[Wallet]:
        """Returns a list of all wallets"""

        return self.repository.get_all()

    def get_wallets_for_user(self, user_id: int, **filters):
        """Returns wallets filtered and sorted for a given user."""

        return self.repository.filter_wallets(user_id=user_id, **filters)

    def get_by_id(self, wallet_id: int, user_id: int) -> Wallet | None:
        """Return a wallet only if it belongs to the user."""

        wallet = self.repository.get_by_id(wallet_id)
        if not wallet or wallet.user_id != user_id:
            raise ValueError("Wallet does not exist or does not belong to you")
        return wallet

    def create(self, user_id: int, name: str, currency="EUR") -> Wallet:
        """Creates a wallet for a user with user_id."""

        if not self.user_repository.get_by_id(user_id):
            raise ValueError("This user does not exist")

        wallet = Wallet(name=name, currency=currency, user_id=user_id)
        return self.repository.create(wallet)

    def delete(self, wallet_id: int, user_id: int) -> None:
        """Deletes a wallet with id from a user with user_id.
        Only works if wallet """

        wallet = self.repository.get_by_id(wallet_id)
        if not wallet and wallet.user_id != user_id:
            raise ValueError("This wallet does not exist or does not belong to you")
        self.repository.delete(wallet)

    def admin_delete(self, wallet_id: int) -> None:
        """Deletes a wallet with wallet_id.
        Requires ADMIN role"""

        wallet = self.repository.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("This wallet does not exist")
        self.repository.delete(wallet)

    def update(self, wallet_id: int, user_id: int, data) -> Wallet | None:
        """Updates a wallet with id of a user with user_id.
        Only works if a wallet belongs to the user with user_id"""

        wallet = self.repository.get_by_id(wallet_id)
        if wallet and wallet.user_id == user_id:
            self.repository.update(wallet, data)
            return
        else:
            raise ValueError("This wallet does not exist or belongs to somebody else")

    def admin_update(self, wallet_id: int, data) -> Wallet | None:
        """Updates a wallet with a specific id.
        Only works for admins"""

        wallet = self.repository.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("This wallet does not exist")
        return self.repository.update(wallet, data)
