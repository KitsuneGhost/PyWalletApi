from datetime import datetime, timezone

from app.auth.revocation_store import RevocationStore
from app.auth.token_provider import TokenProvider


class AuthService:
    def __init__(self, users_repo, hasher, tokens: TokenProvider, revocations: RevocationStore):
        self.users = users_repo
        self.hasher = hasher
        self.tokens = tokens
        self.revocations = revocations

    def login(self, email: str, password: str):
        user = self.users.get_by_email(email)
        if not user or not self.hasher.verify(user.password_hash, password):
            raise ValueError("Invalid credentials")

        access, access_claims = self.tokens.create_access(str(user.id), roles=user.roles)
        refresh, refresh_claims = self.tokens.create_refresh(str(user.id))
        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "Bearer",
            "expires_in": 60 * self.tokens.access_minutes,
        }

    def refresh(self, refresh_token: str):
        payload = self.tokens.verify(refresh_token)
        if payload.get("typ") != "refresh":
            raise ValueError("Not a refresh token")
        if self.revocations.is_revoked(payload["jti"]):
            raise ValueError("Refresh token revoked")

        # rotate refresh tokens (invalidate old, issue new)
        new_access, _ = self.tokens.create_access(payload["sub"])
        new_refresh, new_rclaims = self.tokens.create_refresh(payload["sub"])

        # Revoke old refresh jti
        exp = payload["exp"] - int(datetime.now(timezone.utc).timestamp())
        if exp > 0:
            self.revocations.revoke(payload["jti"], exp)

        return {"access_token": new_access, "refresh_token": new_refresh, "token_type": "Bearer"}

    def logout(self, token_payload: dict):
        # revoke current access jti
        exp = token_payload["exp"] - int(datetime.now(timezone.utc).timestamp())
        if exp > 0:
            self.revocations.revoke(token_payload["jti"], exp)
