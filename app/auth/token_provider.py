from dataclasses import dataclass
from datetime import timedelta, datetime, timezone
import jwt
import uuid
from typing import Optional
from app.exceptions.token_exceptions import TokenError, TokenExpired, TokenInvalid


@dataclass(frozen=True)   # Object Immutability
class TokenConfig:
    issuer: str
    secret: str
    algorithm: str = "HS256"
    access_ttl: timedelta = timedelta(minutes=15)
    refresh_ttl: timedelta = timedelta(days=7)


class TokenProvider:

    def __init__(self, config: TokenConfig):
        self.config = config

        if not config.issuer or config.issuer.strip() == "":
            raise ValueError("Issuer is empty!")

        if not config.secret or config.secret.strip() == "":
            raise ValueError("Secret is empty!")

    def issue_access_token(self, user_id: int) -> str:

        # no roles in the token because of stateful authorization (roles stored in db)

        now = datetime.now(timezone.utc)
        now_ts = int(now.timestamp())                                   # current time in UNIX seconds
        exp_ts = int((now + self.config.access_ttl).timestamp())        # expiry date in UNIX seconds


        # token parameters
        payload = {
            "sub": str(user_id),                                    # subject, user id
            "iss": self.config.issuer,                              # issuer
            "iat": now_ts,                                          # issued at
            "nbf": now_ts,                                          # not before
            "exp": exp_ts,                                          # expires at
            "jti": str(uuid.uuid4()),                               # token id
            "typ": "access",                                        # token type
        }

        token = jwt.encode(payload, self.config.secret, algorithm=self.config.algorithm)

        return token

    def verify(self, token: str, expected_type: str | None = None) -> dict:

        # expected type is optional so the same verification logic can be reused for access and refresh tokens,
        # enforcing the type only when required.

        try:
            payload = jwt.decode(token, self.config.secret,
                                 algorithms=[self.config.algorithm],    # checking algorithm
                                 issuer=self.config.issuer,             # checking issuer
                                 options={"require": ["sub", "iss", "iat", "nbf", "exp", "jti", "typ"]},
                                 )

        # Custom exception classes to decouple auth logic from the Jwt library
        except jwt.ExpiredSignatureError as e:
            raise TokenExpired("Token is expired!") from e
        except jwt.InvalidTokenError as e:
            raise TokenInvalid("Invalid token!") from e

        # type check
        if expected_type is not None and payload.get("typ") != expected_type:
            raise TokenInvalid("Wrong token type")

        # TODO: Implement Exception classes
        return payload

    def issue_refresh_token(self, user_id: int) -> str:

        now = datetime.now(timezone.utc)
        now_ts = int(now.timestamp())
        exp_ts = int((now + self.config.refresh_ttl).timestamp())

        payload = {
            "sub": str(user_id),                    # subject, user id
            "iss": self.config.issuer,              # issuer
            "iat": now_ts,                          # issued at
            "nbf": now_ts,                          # not before
            "exp": exp_ts,                          # expires at
            "jti": str(uuid.uuid4()),               # token id
            "typ": "refresh",                       # token type
        }

        token = jwt.encode(payload, self.config.secret, algorithm=self.config.algorithm)

        return token
