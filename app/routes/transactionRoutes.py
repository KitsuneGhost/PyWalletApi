from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.schemas.transactionSchemas import TransactionResponseSchema, TransferSchema, WithdrawSchema
from app.services.transactionService import TransactionService

transaction_bp = Blueprint("transaction_bp", __name__, url_prefix="/transactions")
withdraw_schema, transfer_schema = WithdrawSchema(), TransferSchema()
transactions_schema = TransactionResponseSchema(many=True)
transaction_schema = TransactionResponseSchema()


def actor():
    return int(get_jwt_identity())


def execute(schema, operation, *ids):
    try:
        data = schema.load(request.get_json(silent=True) or {})
        tx = operation(actor(), *ids, **data)
        return jsonify(status="success", data=transaction_schema.dump(tx)), 201
    except ValidationError as exc:
        return jsonify(status="error", message=exc.messages), 400
    except ValueError as exc:
        return jsonify(status="error", message=str(exc)), 400


@transaction_bp.get("/")
@jwt_required()
def history():
    page = request.args.get("page", 1, type=int)
    per_page = min(request.args.get("per_page", 20, type=int), 100)
    if page < 1 or per_page < 1:
        return jsonify(status="error", message="Invalid pagination"), 400
    result = TransactionService.get_for_user(actor(), page, per_page)
    return jsonify(
        status="success",
        data=transactions_schema.dump(result.items),
        pagination={"page": result.page, "pages": result.pages, "per_page": result.per_page, "total": result.total},
    ), 200


@transaction_bp.post("/wallets/<int:wallet_id>/withdraw")
@jwt_required()
def withdraw(wallet_id):
    return execute(withdraw_schema, TransactionService.withdraw, wallet_id)


@transaction_bp.post("/wallets/<int:wallet_id>/transfer")
@jwt_required()
def transfer(wallet_id):
    return execute(transfer_schema, TransactionService.transfer, wallet_id)
