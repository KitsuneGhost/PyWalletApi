from app.models.wallet import Wallet
from app.repositories.walletRepository import WalletRepository
from app.services.userService import UserService


class WalletService:
    @staticmethod
    def get_wallets_for_user(user_id, **filters):
        """Returns wallets filtered and sorted for a given user."""

        return WalletRepository.filter_wallets(user_id=user_id, **filters)

    @staticmethod
    def get_by_id(wallet_id, user_id):
        """Return a wallet only if it belongs to the user."""

        wallet = WalletRepository.get_by_id(wallet_id)
        if not wallet or wallet.user_id != user_id:
            raise ValueError("Wallet does not exist or does not belong to you")
        return wallet

    @staticmethod
    def create(user_id, name, currency="EUR"):
        """Creates a wallet for a user with user_id."""

        if not UserService.get_by_id(user_id):
            raise ValueError("This user does not exist")

        wallet = Wallet(name=name, currency=currency, user_id=user_id)
        return WalletRepository.create(wallet)

    @staticmethod
    def delete(wallet_id, user_id):
        """Deletes a wallet with id from a user with user_id.
        Only works if wallet """

        wallet = WalletRepository.get_by_id(wallet_id)
        if not wallet and wallet.user_id != user_id:
            raise ValueError("This wallet does not exist or does not belong to you")
        WalletRepository.delete(wallet)

    @staticmethod
    def admin_delete(wallet_id):
        """Deletes a wallet with wallet_id.
        Requires ADMIN role"""

        wallet = WalletRepository.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("This wallet does not exist")
        WalletRepository.delete(wallet)

    @staticmethod
    def update(wallet_id, user_id, data):
        """Updates a wallet with id of a user with user_id.
        Only works if a wallet belongs to the user with user_id"""

        wallet = WalletRepository.get_by_id(wallet_id)
        if wallet and wallet.user_id == user_id:
            WalletRepository.update(wallet, data)
            return
        else:
            raise ValueError("This wallet does not exist or belongs to somebody else")

    @staticmethod
    def admin_update(wallet_id, data):
        """Updates a wallet with a specific id.
        Only works for admins"""

        wallet = WalletRepository.get_by_id(wallet_id)
        if not wallet:
            raise ValueError("This wallet does not exist")
        return WalletRepository.update(wallet, data)
