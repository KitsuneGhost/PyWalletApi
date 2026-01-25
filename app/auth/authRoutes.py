from flask import Blueprint, jsonify, request, g
from marshmallow import ValidationError

from app.auth.authService import AuthService
from app.auth.decorators import Decorator
from app.exceptions.auth_exceptions import InvalidCredentials
from app.exceptions.token_exceptions import TokenExpired, TokenInvalid


def create_auth_routes(
        auth_service: AuthService,
        decorator: Decorator
) -> Blueprint:
    """
    Factory that builds the /auth blueprint with injected dependencies.
    - auth_service: an instance exposing login/refresh/logout
    - decorator: a decorator to guard routes (e.g., @jwt_required)
    """

    auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

    @auth_bp.post('/login')
    def login():

        data = request.get_json(silent=True) or {}
        username = data.get('username')
        password = data.get('password')

        try:

            # checking for empty fields
            if not username or not password:
                raise ValidationError('username or password is required')

            # logging in
            result = auth_service.login(username, password)

            return jsonify(result), 200

        except ValidationError:
            return jsonify({'status': 'error', 'message': 'Bad Request'}), 400

        except InvalidCredentials:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    @auth_bp.post('/refresh')
    def refresh():

        data = request.get_json(silent=True) or {}
        refresh_token = data.get('refresh_token')

        try:

            # checking for empty fields
            if not refresh_token:
                raise ValidationError('refresh_token is required')

            # refreshing token
            result = auth_service.refresh(refresh_token)

            return jsonify(result), 200

        except ValidationError:
            return jsonify({'status': 'error', 'message': 'Bad Request'}), 400

        except (InvalidCredentials, TokenExpired, TokenInvalid):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401


    @auth_bp.post('/logout')
    def logout():

        data = request.get_json(silent=True) or {}
        refresh_token = data.get('refresh_token')

        try:

            # checking for empty fields
            if not refresh_token:
                raise ValidationError('refresh_token is required')

            # logging out
            auth_service.logout(refresh_token)

            return jsonify({'status': 'success', 'message': 'You have been logged out'}), 200

        except ValidationError:
            return jsonify({'status': 'error', 'message': 'Bad Request'}), 400

        except (InvalidCredentials, TokenExpired, TokenInvalid):
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    @auth_bp.get("/me")
    @decorator.jwt_required()
    def me():

        # getting current user
        user = g.current_user

        return jsonify({"id": user.id, "username": user.username, "email": user.email}), 200

    return auth_bp
