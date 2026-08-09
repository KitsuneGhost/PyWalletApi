from datetime import datetime, timezone

from app.extensions.extensions import db


class TokenSession(db.Model):
    __tablename__ = "token_sessions"

    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    revoked_at = db.Column(db.DateTime(timezone=True), nullable=True)

    @property
    def is_revoked(self):
        expires_at = self.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        return self.revoked_at is not None or expires_at <= datetime.now(timezone.utc)
