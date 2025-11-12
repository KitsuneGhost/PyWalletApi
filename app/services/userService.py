from sqlalchemy.exc import IntegrityError

from app.dto.userDto.userUpdateDto import UserUpdateDTO
from app.repositories.userRepository import UserRepository
from app.dto.userDto.userCreateDto import UserCreateDTO
from app.models.user import User


class UserService:

    @staticmethod
    def get_all():
        """Returns all users"""

        return UserRepository.get_all()

    @staticmethod
    def get_by_id(user_id):
        """Returns a user with a specific id"""

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def get_by_email(data):
        """Returns a user with a specific email"""

        user = UserRepository.get_by_email(data["email"])
        if not user:
            raise ValueError("User not found")
        return user

    @staticmethod
    def create(dto: UserCreateDTO):
        """Creates a new user"""

        if UserRepository.get_by_email(dto.email) or UserRepository.get_by_username(dto.username):
            raise ValueError("User with this email or username already exists")

        new_user = User(
            username=dto.username,
            email=dto.email,
            role=dto.role
        )

        new_user.set_password(dto.password)

        try:
            UserRepository.create(new_user)
            return new_user
        except IntegrityError as e:
            raise ValueError("User with this email or username already exists") from e

    @staticmethod
    def delete(user_id: int):
        """Deletes a user"""

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        UserRepository.delete(user)

    @staticmethod
    def update(user_id: int, dto: UserUpdateDTO):
        """Updates a user"""

        existing_user = UserRepository.get_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")

        # Prevent conflicts (optional safety)
        if dto.email is not None:
            other = UserRepository.get_by_email(dto.email)
            if other and other.id != user_id:
                raise ValueError("Email already in use")

        if dto.username is not None:
            other = UserRepository.get_by_username(dto.username)
            if other and other.id != user_id:
                raise ValueError("Username already in use")

        # Convert DTO -> dict (ignore None values)
        data = {
            key: value
            for key, value in dto.__dict__.items()
            if value is not None
        }

        updated_user = UserRepository.update(user_id, data)
        return updated_user
