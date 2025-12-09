from app.extensions.extensions import db
from app.models.user import User


class UserRepository:

    def __init__(self, model: User):
        self.model = model

    def get_all(self) -> list[User]:
        """Returns a list of all users"""

        return self.model.query.all()

    def get_by_id(self, user_id: int) -> User | None:
        """Returns a user with specific id"""

        return self.model.query.get(user_id)

    def get_by_email(self, email) -> User | None:
        """Returns a user with specific email"""

        return self.model.query.filter_by(email=email).first()

    def get_by_username(self, username: str) -> User | None:
        """Returns a user by a specific username"""

        return self.model.query.filter_by(username=username).first()

    def create(self, user: User) -> User:
        """Persists a new user"""
        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    def delete(self, user: User) -> None:
        """Deletes a user"""
        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    def update(self, user_id: int, data: dict) -> User | None:
        """Updates a user with the given fields (skipping None values)"""
        user = self.get_by_id(user_id)
        if not user:
            return None

        try:
            # Update only valid fields and skip None
            for field, value in data.items():
                if value is not None and hasattr(user, field):
                    setattr(user, field, value)

            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e
