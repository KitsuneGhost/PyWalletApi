from app.auth.password_hasher import PasswordHasher
from app.auth.token_provider import TokenProvider
from app.exceptions.auth_exceptions import InvalidCredentials
from app.repositories.userRepository import UserRepository


class AuthService:

    def __init__(
            self,
            user_repo: UserRepository,
            hasher: PasswordHasher,
            token_provider: TokenProvider,
    ):

        self.user_repo = user_repo
        self.hasher = hasher
        self.token_provider = token_provider

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
        user = self.user_repo.get_by_id(user_id)    # checking if user exists

        expires_at = int(payload["exp"])
        token_id = int(payload["jti"])

        if not user:
            raise InvalidCredentials("Invalid credentials!")

        # issue new access token
        access_token = self.token_provider.issue_access_token(user.id)

        return {"access_token": access_token}
