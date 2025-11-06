from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.schemas.userSchemas.UserCreateSchema import UserCreateSchema
from app.schemas.userSchemas.UserResponseSchema import UserResponseSchema
from app.schemas.userSchemas.UserUpdateSchema import UserUpdateSchema
from app.services.userService import UserService

user_bp = Blueprint("user_bp", __name__, url_prefix='/users')

user_response = UserResponseSchema()
users_response = UserResponseSchema(many=True)
user_create = UserCreateSchema()
user_update = UserUpdateSchema()


@user_bp.route("/", methods=["GET"])
def get_all():

    """
    Returns a list of all users.
    Validates data via Marshmallow schemas.
    """

    # Retrieve the list of all users from the service
    users = UserService.get_all()

    # Serialize data and return
    return users_response.jsonify(users), 200


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_by_id(user_id):

    """
    Returns a user with a specific id.
    Validates data via Marshmallow schemas.
    :param user_id: user ID
    """

    try:
        # Get user from the service layer
        user = UserService.get_by_id(user_id)

        # Serialize data and return
        return user_response.jsonify(user), 200

    except ValueError as e:
        # Logical or service-level errors (e.g., user not found)
        return jsonify({'status': 'error', 'message': str(e)}), 404


@user_bp.route("/create", methods=["POST"])
def create():

    """
    Creates and returns a new user.
    Validates data via Marshmallow schemas.
    """

    json_data = request.get_json()
    if not json_data:
        return jsonify({'status': 'error', 'message': 'No input data provided'}), 400
    try:

        # Validate input using UserUpdateSchema (DTO)
        data = user_create.load(json_data)

        # Create a new user
        new_user = UserService.create(data)

        # Serialize data and return
        return user_response.jsonify(new_user), 201

    except ValidationError as err:
        # Thrown by Marshmallow when .load() fails.
        return jsonify({'status': 'error', 'message': err.messages}), 400

    except ValueError as e:
        # Thrown manually by UserService when something logical fails
        return jsonify({'status': 'error', 'message': str(e)}), 400

    except IntegrityError:
        # when a database constraint fails
        return jsonify({'status': 'error', 'message': 'Duplicate email or username'}), 409


@user_bp.route("/<int:user_id>", methods=["PUT"])
def update(user_id):

    """
    Updates a user. Accepts updates to Username, Email, Password and Role.
    Validates data via Marshmallow schemas.
    :param user_id: User ID
    """

    json_data = request.get_json()

    if not json_data:
        return jsonify({'status': 'error', 'message': 'No input data provided'}), 400

    try:
        # Validate input using UserUpdateSchema (DTO)
        data = user_update.load(json_data)

        # Pass validated data to service
        upd_user = UserService.update(user_id, data)

        # Serialize updated user and return
        return user_response.jsonify(upd_user), 200

    except ValidationError as err:
        # Marshmallow validation errors (field format, missing data, etc.)
        return jsonify({'status': 'error', 'message': err.messages}), 400

    except ValueError as e:
        # Logical or service-level errors (e.g., user not found)
        return jsonify({'status': 'error', 'message': str(e)}), 404

    except IntegrityError:
        # DB constraint violations (e.g., duplicate email)
        return jsonify({'status': 'error', 'message': 'Database constraint error'}), 409


@user_bp.route("/<int:user_id>", methods=["DELETE"])
def delete(user_id):

    """
    Deletes a user.
    Validates user_id before performing an operation
    :param user_id: user ID
    """

    try:
        # Delete user
        UserService.delete(user_id)
        return jsonify({'status': 'success', 'message': 'User deleted successfully'}), 200

    except ValueError as e:
        # Logical or service-level errors (e.g., user not found)
        return jsonify({'status': 'error', 'message': str(e)}), 404
