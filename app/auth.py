from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt, get_jwt_identity, verify_jwt_in_request


def current_user_id() -> int:
    return int(get_jwt_identity())


def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        verify_jwt_in_request()
        if get_jwt().get("role") != "ADMIN":
            return jsonify(status="error", message="Administrator access required"), 403
        return fn(*args, **kwargs)
    return wrapped


def self_or_admin(user_id: int) -> bool:
    return current_user_id() == user_id or get_jwt().get("role") == "ADMIN"
