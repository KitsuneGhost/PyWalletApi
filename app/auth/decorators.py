from functools import wraps
from flask import request, jsonify, g

def jwt_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        parts = header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"status": "error", "message": "Missing/invalid Authorization header"}), 401

        token = parts[1]
        try:
            payload = wrapper.tokens.verify(token)
        except Exception:
            return jsonify({"status": "error", "message": "Invalid or expired token"}), 401

        if wrapper.revocations.is_revoked(payload["jti"]):
            return jsonify({"status": "error", "message": "Token revoked"}), 401

        user = wrapper.users.get_by_id(int(payload["sub"]))
        if not user:
            return jsonify({"status": "error", "message": "User not found"}), 404

        g.current_user = user
        g.current_claims = payload
        return f(*args, **kwargs)

    # dependencies injected at blueprint registration time
    wrapper.tokens = None
    wrapper.revocations = None
    wrapper.users = None
    return wrapper

def roles_required(*required_roles):
    def decorator(f):
        @wraps(f)
        def inner(*args, **kwargs):
            claims = getattr(g, "current_claims", {}) or {}
            roles = set(claims.get("roles", []))
            if not set(required_roles).issubset(roles):
                from flask import jsonify
                return jsonify({"status": "error", "message": "Forbidden"}), 403
            return f(*args, **kwargs)
        return inner
    return decorator