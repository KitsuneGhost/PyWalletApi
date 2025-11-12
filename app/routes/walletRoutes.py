from flask import Blueprint

from app.schemas.walletSchemas import WalletCreateSchema
from app.schemas.walletSchemas import WalletResponseSchema
from app.schemas.walletSchemas import WalletUpdateSchema
from app.services.walletService import WalletService

wallet_bp = Blueprint("wallet_bp", __name__, url_prefix='/wallets')

wallet_response = WalletResponseSchema()
wallets_response = WalletResponseSchema(many=True)
wallet_create = WalletCreateSchema()
wallet_update = WalletUpdateSchema()


@wallet_bp.route("/", methods=["GET"])
def get_all():

    """
        Returns a list of all users.
        Validates data via Marshmallow schemas.
        """

    # Retrieve the list of all wallets from the service
    wallets = WalletService.get_all()

    # return data
    return wallets_response.jsonify(wallets)
