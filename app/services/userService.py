from sqlalchemy.exc import IntegrityError

from app.dto.userDTOs import UserUpdateDTO
from app.repositories.userRepository import UserRepository
from app.dto.userDTOs import UserCreateDTO
from app.models.user import User


class UserService:

    @staticmethod
    def authenticate(email, password):
        user = UserRepository.get_by_email(email)
        if user and user.check_password(password):
            return user
        return None

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

        email = dto.email.strip().lower()
        username = dto.username.strip()
        if UserRepository.get_by_email(email) or UserRepository.get_by_username(username):
            raise ValueError("User with this email or username already exists")
        new_user = User(username=username, email=email, role="USER")

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

        if "email" in data:
            data["email"] = data["email"].strip().lower()
        if "username" in data:
            data["username"] = data["username"].strip()
        if "password" in data:
            existing_user.set_password(data.pop("password"))

        updated_user = UserRepository.update(user_id, data)
        return updated_user
