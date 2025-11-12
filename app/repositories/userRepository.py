from app.extensions.extensions import db
from app.models.user import User


class UserRepository:

    @staticmethod
    def get_all():
        """Returns a list of all users"""

        return User.query.all()

    @staticmethod
    def get_by_id(user_id: int):
        """Returns a user with specific id"""

        return User.query.get(user_id)

    @staticmethod
    def get_by_email(email):
        """Returns a user with specific email"""

        return User.query.filter_by(email=email).first()

    @staticmethod
    def get_by_username(username: str):
        """Returns a user by a specific username"""

        return User.query.filter_by(username=username).first()

    @staticmethod
    def create(user: User):
        """Creates a new user"""

        try:
            db.session.add(user)
            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def delete(user: User):
        """Deletes a user"""

        try:
            db.session.delete(user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

    @staticmethod
    def update(user_id: int, data: dict):
        """Updates a user"""

        user = User.query.get(user_id)
        if not user:
            return None

        try:
            # Update only valid fields and skip None
            for field, value in data.items():
                if value is not None and hasattr(User, field):
                    setattr(user, field, value)

            db.session.commit()
            return user
        except Exception as e:
            db.session.rollback()
            raise e
