from datetime import datetime, timezone

from app.extensions.extensions import db


class TokenRevocation(db.Model):

    """
    Stores revoked JWTs (by jti) for refresh token rotation.
    """

    __tablename__ = "token_revocations"

    jti = db.Column(db.String(255), primary_key=True)

    expires_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        index=True
    )

    revoked_at = db.Column(
        db.DateTime(timezone=True),
        default=datetime.now(timezone.utc),
        nullable=False
    )

