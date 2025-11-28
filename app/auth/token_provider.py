import jwt, uuid
from datetime import datetime, timedelta, timezone

class TokenProvider:
    def __init__(self, secret: str, issuer: str, access_minutes: int, refresh_days: int):
        self.secret = secret
        self.issuer = issuer
        self.access_minutes = access_minutes
        self.refresh_days = refresh_days
        self.algorithm = "HS256"

    def _now(self):
        return datetime.now(timezone.utc)

    def _claims_common(self, sub: str):
        now = self._now()
        return {
            "iss": self.issuer,
            "sub": sub,
            "iat": int(now.timestamp()),
            "nbf": int(now.timestamp()),
            "jti": str(uuid.uuid4()),
        }

    def create_access(self, sub: str, roles: list[str] | None = None):
        claims = self._claims_common(sub)
        claims["exp"] = int((self._now() + timedelta(minutes=self.access_minutes)).timestamp())
        if roles: claims["roles"] = roles
        return jwt.encode(
            claims,
            self.secret,
            algorithm=self.algorithm
        ), claims

    def create_refresh(self, sub: str):
        claims = self._claims_common(sub)
        claims["exp"] = int((self._now() + timedelta(days=self.refresh_days)).timestamp())
        claims["typ"] = "refresh"
        return jwt.encode(
            claims,
            self.secret,
            algorithm=self.algorithm
        ), claims

    def verify(self, token: str):
        # raises on invalid signature/expired
        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            options={"require": ["exp","iat","nbf","sub","jti","iss"]}
        )
