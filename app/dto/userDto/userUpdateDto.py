from dataclasses import dataclass
from typing import Optional


@dataclass
class UserUpdateDTO:
    """DTO for updating a user"""

    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None
