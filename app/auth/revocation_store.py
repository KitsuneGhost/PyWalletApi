from datetime import datetime, timezone

from app.extensions.extensions import db
from app.models.token_revocation import TokenRevocation


class RevocationStore:

    def __init__(self, model=TokenRevocation):
        self.model = model

    def is_revoked(self, jti: str) -> bool:

        # getting token from revocation table
        token = self.model.query.get(jti)

        # checking if token is in the table and is not expired
        if token and token.expires_at > datetime.now(timezone.utc):
            return True

        return False

    def revoke(self, jti: str, expires_at: datetime) -> None:

        token = self.model.query.get(jti)

        #  checking id token is in the table
        if token:
            return None

        try:
            # token revocation (adding token to the table)
            rev_token = self.model(
                jti=jti,
                expires_at=expires_at,
                revoked_at=datetime.now(timezone.utc)
            )

            db.session.add(rev_token)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

        return None
