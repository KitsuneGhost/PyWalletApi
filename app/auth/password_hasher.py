from werkzeug.security import generate_password_hash, check_password_hash

class PasswordHasher:

    def hash_password(self, raw: str) -> str:
        return generate_password_hash(raw)

    def verify_password(self, hashed: str, raw: str) -> bool:
        return check_password_hash(hashed, raw)
