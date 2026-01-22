from datetime import datetime, timezone

from app.auth.password_hasher import PasswordHasher
from app.auth.revocation_store import RevocationStore
from app.auth.token_provider import TokenProvider
from app.exceptions.auth_exceptions import InvalidCredentials
from app.exceptions.token_exceptions import TokenExpired
from app.repositories.userRepository import UserRepository


class AuthService:

    def __init__(
            self,
            user_repo: UserRepository,
            hasher: PasswordHasher,
            token_provider: TokenProvider,
            revocations: RevocationStore
    ):

        self.user_repo = user_repo
        self.hasher = hasher
        self.token_provider = token_provider
        self.revocations = revocations

    def login(self, username: str, password: str) -> dict:
        user = self.user_repo.get_by_username(username)  # fetching user from db

        # verifying credentials
        if not user or not self.hasher.verify_password(user.hashed_password, password):
            raise InvalidCredentials("Invalid credentials!")

        access_token = self.token_provider.issue_access_token(user.id)  # access token
        refresh_token = self.token_provider.issue_refresh_token(user.id)  # refresh token

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def refresh(self, refresh_token: str) -> dict:
        # verifying token and extracting payload
        payload = self.token_provider.verify(refresh_token, expected_type="refresh")

        user_id = int(payload["sub"])
        token_id = payload["jti"]

        # transforming from UNIX seconds to datetime
        expires_at = datetime.fromtimestamp(int(payload["exp"]), tz=timezone.utc)

        user = self.user_repo.get_by_id(user_id)

        # checking if user exists
        if not user:
            raise InvalidCredentials("Invalid credentials!")

        # checking if refresh token is revoked
        # raising InvalidCredentials instead of InvalidToken to prevent the leak of deatails
        if self.revocations.is_revoked(token_id):
            raise InvalidCredentials("Token is Revoked!")

        # revoking refresh token
        self.revocations.revoke(token_id, expires_at)

        # issue new access token
        access_token = self.token_provider.issue_access_token(user.id)
        new_refresh_token = self.token_provider.issue_refresh_token(user.id)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token
        }
