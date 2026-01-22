class AuthException(Exception):
    pass

class UnauthorizedAttempt(AuthException): ...