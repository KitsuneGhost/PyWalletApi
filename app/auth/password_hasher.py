from werkzeug.security import generate_password_hash, check_password_hash

class PasswordHasherService:

    # Never store raw passwords; hash on signup, verify on login.

    def hash(self, raw: str) -> str:
        return generate_password_hash(raw)

    def verify(self, hashed: str, raw: str) -> bool:
        return check_password_hash(hashed, raw)