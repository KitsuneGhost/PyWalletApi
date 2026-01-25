from app.dto.userDTOs import UserUpdateDTO
from app.repositories.userRepository import UserRepository


class UserService:

    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_all(self):
        """Returns all users"""
        return self.repository.get_all()

    def get_by_id(self, user_id):
        """Returns a user with a specific id"""

        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def get_by_email(self, data):
        """Returns a user with a specific email"""

        user = self.repository.get_by_email(data["email"])
        if not user:
            raise ValueError("User not found")
        return user

    def delete(self, user_id: int):
        """Deletes a user"""

        user = self.repository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        self.repository.delete(user)

    def update(self, user_id: int, dto: UserUpdateDTO):
        """Updates a user"""

        existing_user = self.repository.get_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")

        # Prevent conflicts (optional safety)
        if dto.email is not None:
            other = self.repository.get_by_email(dto.email)
            if other and other.id != user_id:
                raise ValueError("Email already in use")

        if dto.username is not None:
            other = self.repository.get_by_username(dto.username)
            if other and other.id != user_id:
                raise ValueError("Username already in use")

        # Convert DTO -> dict (ignore None values)
        data = {
            key: value
            for key, value in dto.__dict__.items()
            if value is not None
        }

        updated_user = self.repository.update(user_id, data)
        return updated_user
