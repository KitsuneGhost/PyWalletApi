from dataclasses import dataclass


@dataclass
class UserCreateDTO:
    """DTO for creating a new user"""

    username: str
    email: str
    password: str
    role: str
