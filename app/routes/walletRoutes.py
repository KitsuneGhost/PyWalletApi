from flask import Blueprint, jsonify

from app.schemas.walletSchemas import WalletCreateSchema
from app.schemas.walletSchemas import WalletResponseSchema
from app.schemas.walletSchemas import WalletUpdateSchema
from app.services.walletService import WalletService


def create_wallet_routes (
        wallet_service,                      # <- instance of WalletService
        wallet_response_schema: WalletResponseSchema | None = None,
        wallets_response_schema: WalletResponseSchema | None = None,
        wallet_create_schema: WalletCreateSchema | None = None,
        wallet_update_schema: WalletUpdateSchema | None = None
) -> Blueprint:

    """
        Factory that builds the /wallets blueprint with injected dependencies.
        - wallet_service: an instance exposing get_all/get_by_id/create/update/delete
        - schemas: optional pre-built schema instances (useful for testing); defaults created if None
        """

    wallet_bp = Blueprint("wallet_bp", __name__, url_prefix='/wallets')

    _wallet_response = wallet_response_schema or WalletResponseSchema()
    _wallets_response = wallets_response_schema or WalletResponseSchema(many=True)
    _wallet_create = wallet_create_schema or WalletCreateSchema()
    _wallet_update = wallet_update_schema or WalletUpdateSchema()

    @wallet_bp.get("/")
    def get_all():

        """
            Returns a list of all users.
            Validates data via Marshmallow schemas.
            """

        try:
            # Retrieve the list of all wallets from the service
            wallets = WalletService.get_all()

            # return data
            return _wallets_response.jsonify(wallets)

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500


    return wallet_bp