from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.schemas.walletSchemas import WalletCreateSchema, WalletResponseSchema, WalletUpdateSchema
from app.services.walletService import WalletService

wallet_bp = Blueprint("wallet_bp", __name__, url_prefix="/wallets")
wallet_response = WalletResponseSchema()
wallets_response = WalletResponseSchema(many=True)
wallet_create = WalletCreateSchema()
wallet_update = WalletUpdateSchema()


def uid():
    return int(get_jwt_identity())


def failure(exc, status=400):
    return jsonify(status="error", message=str(exc)), status


@wallet_bp.get("/")
@jwt_required()
def get_all():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    if page < 1 or per_page < 1:
        return failure("Invalid pagination", 400)
    wallets = WalletService.get_wallets_for_user(uid(), page=page, per_page=per_page)
    return jsonify(status="success", data=wallets_response.dump(wallets.items), pagination={"page": page, "pages": wallets.pages, "total": wallets.total}), 200


@wallet_bp.post("/")
@jwt_required()
def create():
    try:
        data = wallet_create.load(request.get_json(silent=True) or {})
        wallet = WalletService.create(uid(), data["name"], data["currency"])
        return jsonify(status="success", data=wallet_response.dump(wallet)), 201
    except ValidationError as exc:
        return jsonify(status="error", message=exc.messages), 400
    except ValueError as exc:
        return failure(exc, 409)


@wallet_bp.get("/<int:wallet_id>")
@jwt_required()
def get_one(wallet_id):
    try:
        return jsonify(status="success", data=wallet_response.dump(WalletService.get_by_id(wallet_id, uid()))), 200
    except ValueError as exc:
        return failure(exc, 404)


@wallet_bp.patch("/<int:wallet_id>")
@jwt_required()
def update(wallet_id):
    try:
        data = wallet_update.load(request.get_json(silent=True) or {})
        if not data:
            return failure("No valid fields provided")
        wallet = WalletService.update(wallet_id, uid(), data)
        return jsonify(status="success", data=wallet_response.dump(wallet)), 200
    except ValidationError as exc:
        return jsonify(status="error", message=exc.messages), 400
    except ValueError as exc:
        return failure(exc, 404)


@wallet_bp.delete("/<int:wallet_id>")
@jwt_required()
def delete(wallet_id):
    try:
        WalletService.delete(wallet_id, uid())
        return "", 204
    except ValueError as exc:
        return failure(exc, 409 if "zero balance" in str(exc) else 404)
