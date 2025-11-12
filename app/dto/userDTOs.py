from dataclasses import dataclass
from typing import Optional

from sqlalchemy import DateTime


@dataclass
class UserCreateDTO:
    """DTO for creating a new user"""

    username: str
    email: str
    password: str
    role: str


@dataclass
class UserResponseDTO:
    """DTO for user responses"""

    id: int
    username: str
    email: str
    role: str
    created_at: DateTime


@dataclass
class UserUpdateDTO:
    """DTO for updating a user"""

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
