from flask import Blueprint, request, jsonify, g

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

def create_auth_routes(auth_service, jwt_required_decorator):
    @auth_bp.post("/login")
    def login():
        data = request.get_json() or {}
        try:
            result = auth_service.login(data.get("email",""), data.get("password",""))
            return jsonify(result), 200
        except ValueError:
            return jsonify({"status": "error", "message": "Invalid credentials"}), 401

    @auth_bp.post("/refresh")
    def refresh():
        data = request.get_json() or {}
        try:
            result = auth_service.refresh(data.get("refresh_token",""))
            return jsonify(result), 200
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400

    @auth_bp.post("/logout")
    @jwt_required_decorator
    def logout():
        claims = getattr(g, "current_claims", {})
        auth_service.logout(claims)
        return jsonify({"status": "success", "message": "logged out"}), 200

    return auth_bp
