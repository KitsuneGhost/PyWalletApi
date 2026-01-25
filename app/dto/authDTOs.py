from dataclasses import dataclass


@dataclass
class RegisterDTO:
    """DTO for creating a new user"""

    username: str
    email: str
    password: str
