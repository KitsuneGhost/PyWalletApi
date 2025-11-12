from dataclasses import dataclass

from sqlalchemy import DateTime


@dataclass
class UserResponseDTO:
    """DTO for user responses"""

    id: int
    username: str
    email: str
    role: str
    created_at: DateTime
