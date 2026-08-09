from flask import Blueprint, current_app, jsonify, request
from datetime import datetime, timezone
from uuid import uuid4

from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt, get_jwt_identity, jwt_required
from marshmallow import ValidationError

from app.auth import admin_required, self_or_admin
from app.extensions.extensions import db
from app.models.tokenSession import TokenSession
from app.dto.userDTOs import UserCreateDTO, UserUpdateDTO
from app.schemas.userSchemas import UserCreateSchema, UserResponseSchema, UserUpdateSchema
from app.services.userService import UserService

user_bp = Blueprint("user_bp", __name__, url_prefix="/users")
user_response_schema = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()


def error(message, status):
    return jsonify(status="error", message=message), status


@user_bp.post("/register")
def register():
    try:
        data = user_create_schema.load(request.get_json(silent=True) or {})
        user = UserService.create(UserCreateDTO(**data))
        return jsonify(status="success", data=user_response_schema.dump(user)), 201
    except ValidationError as exc:
        return error(exc.messages, 400)
    except ValueError as exc:
        return error(str(exc), 409)


@user_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = data.get("password", "")
    user = UserService.authenticate(email, password)
    if not user:
        return error("Invalid credentials", 401)
    session_id = str(uuid4())
    expires_at = datetime.now(timezone.utc) + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    db.session.add(TokenSession(id=session_id, user_id=user.id, expires_at=expires_at))
    db.session.commit()
    claims = {"role": user.role, "sid": session_id}
    return jsonify(
        status="success",
        access_token=create_access_token(identity=str(user.id), additional_claims=claims),
        refresh_token=create_refresh_token(identity=str(user.id), additional_claims=claims),
    ), 200


@user_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user = UserService.get_by_id(int(get_jwt_identity()))
    claims = {"role": user.role, "sid": get_jwt()["sid"]}
    return jsonify(status="success", access_token=create_access_token(identity=str(user.id), additional_claims=claims)), 200


@user_bp.post("/logout")
@jwt_required(verify_type=False)
def logout():
    session = db.session.get(TokenSession, get_jwt()["sid"])
    if session and session.revoked_at is None:
        session.revoked_at = datetime.now(timezone.utc)
        db.session.commit()
    return "", 204


@user_bp.get("/")
@admin_required
def get_all():
    return jsonify(status="success", data=users_response_schema.dump(UserService.get_all())), 200


@user_bp.get("/me")
@jwt_required()
def me():
    user = UserService.get_by_id(int(get_jwt_identity()))
    return jsonify(status="success", data=user_response_schema.dump(user)), 200


@user_bp.get("/<int:user_id>")
@jwt_required()
def get_by_id(user_id):
    if not self_or_admin(user_id):
        return error("Forbidden", 403)
    try:
        return jsonify(status="success", data=user_response_schema.dump(UserService.get_by_id(user_id))), 200
    except ValueError as exc:
        return error(str(exc), 404)


@user_bp.patch("/<int:user_id>")
@jwt_required()
def update(user_id):
    if not self_or_admin(user_id):
        return error("Forbidden", 403)
    try:
        data = user_update_schema.load(request.get_json(silent=True) or {})
        if not data:
            return error("No valid fields provided", 400)
        user = UserService.update(user_id, UserUpdateDTO(**data))
        return jsonify(status="success", data=user_response_schema.dump(user)), 200
    except ValidationError as exc:
        return error(exc.messages, 400)
    except ValueError as exc:
        return error(str(exc), 409 if "use" in str(exc).lower() else 404)


@user_bp.delete("/<int:user_id>")
@jwt_required()
def delete(user_id):
    if not self_or_admin(user_id):
        return error("Forbidden", 403)
    try:
        UserService.delete(user_id)
        return "", 204
    except ValueError as exc:
        return error(str(exc), 404)
