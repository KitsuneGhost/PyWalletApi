from functools import wraps
from flask import request, jsonify, g

from app.auth.token_provider import TokenProvider
from app.exceptions.decorator_exceptions import UnauthorizedAttempt
from app.exceptions.token_exceptions import TokenExpired, TokenInvalid
from app.repositories.userRepository import UserRepository


class Decorator:

    def __init__(self, token_provider: TokenProvider, user_repo: UserRepository):
        self.token_provider = token_provider
        self.user_repo = user_repo

    def _get_bearer_token(self) -> str:
        """
        Get bearer token from request
        """

        # get a bearer token from request
        auth = request.headers.get("Authorization")
        if not auth:
            raise UnauthorizedAttempt("Bearer token required")

        # checking that it starts with 'Bearer' (it should)
        if not auth.startswith("Bearer "):
            raise UnauthorizedAttempt("Bearer token required")

        token = auth.split(" ", 1)[1].strip()
        # checking that jwt isn't empty
        if not token:
            raise UnauthorizedAttempt("Bearer token required")

        return token

    def jwt_required(self):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                try:
                    token = self._get_bearer_token()
                    payload = self.token_provider.verify(token, expected_type="access")
                    user_id = int(payload["sub"])
                    user = self.user_repo.get_by_id(user_id)
                    if not user:
                        return jsonify({"error": "User doesnt exist"}), 401
                    g.current_user = user
                    g.token_payload = payload
                    return fn(*args, **kwargs)
                except UnauthorizedAttempt:
                    return jsonify({"error": "Unauthorized"}), 401
                except TokenExpired:
                    return jsonify({"error": "Token is expired"}), 401
                except TokenInvalid:
                    return jsonify({"error": "Token is invalid"}), 401
                except ValueError:
                    return jsonify({"error": "Invalid subject claim"}), 401
                except Exception as e:
                    return jsonify({"error": "Internal server error"}), 500

            return wrapper

        return decorator

