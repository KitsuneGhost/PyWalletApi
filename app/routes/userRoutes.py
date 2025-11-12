from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from app.dto.userDto.userCreateDto import UserCreateDTO
from app.dto.userDto.userResponseDto import UserResponseDTO
from app.dto.userDto.userUpdateDto import UserUpdateDTO
from app.schemas.userSchemas.userCreateSchema import UserCreateSchema
from app.schemas.userSchemas.userResponseSchema import UserResponseSchema
from app.schemas.userSchemas.userUpdateSchema import UserUpdateSchema
from app.services.userService import UserService

user_bp = Blueprint("user_bp", __name__, url_prefix='/users')

user_response_schema = UserResponseSchema()
users_response_schema = UserResponseSchema(many=True)
user_create_schema = UserCreateSchema()
user_update_schema = UserUpdateSchema()


@user_bp.route("/", methods=["GET"])
def get_all():

    """
    Returns a list of all users.
    Validates data via Marshmallow schemas.
    """

    try:
        # Fetch ORM users from service
        users = UserService.get_all()

        # Map ORM models -> DTOs
        user_dtos = [
            UserResponseDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                created_at=user.created_at
            )
            for user in users
        ]

        # Serialize DTOs -> JSON using Marshmallow
        result = users_response_schema.dump(user_dtos, many=True)

        return jsonify({'status': 'success', 'data': result}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@user_bp.route("/<int:user_id>", methods=["GET"])
def get_by_id(user_id):

    """
    Returns a user with a specific id.
    Validates data via Marshmallow schemas.
    :param user_id: user ID
    """

    try:
        # Fetch ORM users from service
        user = UserService.get_by_id(user_id)

        # Map ORM models -> DTOs
        user_dto = UserResponseDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                created_at=user.created_at
        )

        # Serialize DTO -> JSON using Marshmallow
        result = user_response_schema.dump(user_dto)

        return jsonify({'status': 'success', 'data': result}), 200

    except ValueError as e:
        # Logical or service-level errors (e.g., user not found)
        return jsonify({'status': 'error', 'message': str(e)}), 404

    except Exception as e:
        # unexpected server error
        return jsonify({'status': 'error', 'message': 'Internal server error'}), 500


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
        # Validate and deserialize input
        validated_data = user_create_schema.load(json_data)

        # Map dict -> DTO
        user_dto = UserCreateDTO(**validated_data)

        # Pass DTO to service
        new_user = UserService.create(user_dto)

        return jsonify({'status': 'success', 'message': {
            'id': new_user.id,
            'username': new_user.username,
            'email': new_user.email,
            'role': new_user.role
        }}), 201

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
        # Validate input using UserUpdateSchema
        data = user_update_schema.load(json_data)

        # Map dict -> DTO
        user_upd_dto = UserUpdateDTO(**data)

        # Pass validated data to service
        upd_user = UserService.update(user_id, user_upd_dto)

        # Map model -> UserResponseDTO
        user_resp_dto = UserResponseDTO(
            id=upd_user.id,
            username=upd_user.username,
            email=upd_user.email,
            role=upd_user.role,
            created_at=upd_user.created_at
        )

        # Serialize ResponseDTO -> JSON
        result = user_response_schema.dump(user_resp_dto)

        return jsonify({'status': 'success', 'data': result}), 200

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
