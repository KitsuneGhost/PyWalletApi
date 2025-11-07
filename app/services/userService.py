from sqlalchemy.exc import IntegrityError

from app.repositories.userRepository import UserRepository
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
    def create(data):
        """Creates a new user"""

        if UserRepository.get_by_email(data["email"]) or UserRepository.get_by_username(data["username"]):
            raise ValueError("User with this email or username already exists")

        new_user = User(username=data["username"], email=data["email"])
        new_user.set_password(data["password"])
        try:
            UserRepository.create(new_user)
            return new_user
        except IntegrityError as e:
            raise ValueError("User with this email or username already exists") from e

    @staticmethod
    def delete(user_id):
        """Deletes a user"""

        user = UserRepository.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        UserRepository.delete(user)

    @staticmethod
    def update(user_id, data):
        """Updates a user"""

        existing_user = UserRepository.get_by_id(user_id)
        if not existing_user:
            raise ValueError("User not found")

        # Prevent conflicts (optional safety)
        if "email" in data:
            other = UserRepository.get_by_email(data["email"])
            if other and other.id != user_id:
                raise ValueError("Email already in use")

        if "username" in data:
            other = UserRepository.get_by_username(data["username"])
            if other and other.id != user_id:
                raise ValueError("Username already in use")

        updated_user = UserRepository.update(user_id, data)
        return updated_user
