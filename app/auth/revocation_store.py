from datetime import datetime

from sqlalchemy import text


class RevocationStore:
    def __init__(self, session):  # SQLAlchemy session
        self.session = session

    def revoke(self, jti: str, expires_at: datetime):
        self.session.execute(
            text(
                "INSERT INTO token_revocations (jti, expires_at) VALUES (:jti, :exp) ON CONFLICT (jti) DO NOTHING"),
            {"jti": jti, "exp": expires_at}
        )
        self.session.commit()

    def is_revoked(self, jti: str) -> bool:
        row = self.session.execute(
            text("SELECT 1 FROM token_revocations WHERE jti=:jti LIMIT 1"),
            {"jti": jti}
        ).first()
        return row is not None