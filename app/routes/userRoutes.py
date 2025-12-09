from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

# Import DTOs & Schemas
from app.dto.userDTOs import UserCreateDTO, UserResponseDTO, UserUpdateDTO
from app.schemas.userSchemas import UserCreateSchema, UserResponseSchema, UserUpdateSchema


def create_user_routes (
    user_service,                      # <- instance of UserService
    user_response_schema: UserResponseSchema | None = None,
    users_response_schema: UserResponseSchema | None = None,
    user_create_schema: UserCreateSchema | None = None,
    user_update_schema: UserUpdateSchema | None = None,
) -> Blueprint:

    """
    Factory that builds the /users blueprint with injected dependencies.
    - user_service: an instance exposing get_all/get_by_id/create/update/delete
    - schemas: optional pre-built schema instances (useful for testing); defaults created if None
    """

    user_bp = Blueprint("user_bp", __name__, url_prefix="/users")

    # Instantiate schemas if not provided
    _user_response_schema = user_response_schema or UserResponseSchema()
    _users_response_schema = users_response_schema or UserResponseSchema(many=True)
    _user_create_schema = user_create_schema or UserCreateSchema()
    _user_update_schema = user_update_schema or UserUpdateSchema()

    @user_bp.get("/")
    def get_all():

        """
        Returns a list of all users.
        Validates/serializes via Marshmallow schemas.
        """

        try:
            # Fetch ORM users from service
            users = user_service.get_all()

            # Map ORM models -> DTOs
            user_dtos = [
                UserResponseDTO(
                    id=u.id,
                    username=u.username,
                    email=u.email,
                    role=u.role,
                    created_at=u.created_at,
                )
                for u in users
            ]

            # Serialize DTOs -> JSON using Marshmallow
            result = _users_response_schema.dump(user_dtos)
            return jsonify({"status": "success", "data": result}), 200

        except Exception as e:
            return jsonify({"status": "error", "message": str(e)}), 500

    @user_bp.get("/<int:user_id>")
    def get_by_id(user_id: int):
        """
        Returns a user with a specific id.
        """
        try:
            user = user_service.get_by_id(user_id)

            user_dto = UserResponseDTO(
                id=user.id,
                username=user.username,
                email=user.email,
                role=user.role,
                created_at=user.created_at,
            )

            result = _user_response_schema.dump(user_dto)
            return jsonify({"status": "success", "data": result}), 200

        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except Exception:
            return jsonify({"status": "error", "message": "Internal server error"}), 500

    @user_bp.post("/create")
    def create():
        """
        Creates and returns a new user.
        Validates data via Marshmallow schemas.
        """
        json_data = request.get_json()
        if not json_data:
            return jsonify({"status": "error", "message": "No input data provided"}), 400

        try:
            # Validate and deserialize input
            validated = _user_create_schema.load(json_data)

            # Map dict -> DTO
            user_dto = UserCreateDTO(**validated)

            # Pass DTO to service
            new_user = user_service.create(user_dto)

            return (
                jsonify(
                    {
                        "status": "success",
                        "message": {
                            "id": new_user.id,
                            "username": new_user.username,
                            "email": new_user.email,
                            "role": new_user.role,
                        },
                    }
                ),
                201,
            )

        except ValidationError as err:
            return jsonify({"status": "error", "message": err.messages}), 400
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 400
        except IntegrityError:
            return (
                jsonify(
                    {"status": "error", "message": "Duplicate email or username"}
                ),
                409,
            )

    @user_bp.put("/<int:user_id>")
    def update(user_id: int):
        """
        Updates a user. Accepts updates to Username, Email, Password and Role.
        """
        json_data = request.get_json()
        if not json_data:
            return jsonify({"status": "error", "message": "No input data provided"}), 400

        try:
            data = _user_update_schema.load(json_data)
            user_upd_dto = UserUpdateDTO(**data)

            upd_user = user_service.update(user_id, user_upd_dto)

            user_resp_dto = UserResponseDTO(
                id=upd_user.id,
                username=upd_user.username,
                email=upd_user.email,
                role=upd_user.role,
                created_at=upd_user.created_at,
            )
            result = _user_response_schema.dump(user_resp_dto)

            return jsonify({"status": "success", "data": result}), 200

        except ValidationError as err:
            return jsonify({"status": "error", "message": err.messages}), 400
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404
        except IntegrityError:
            return (
                jsonify(
                    {"status": "error", "message": "Database constraint error"}
                ),
                409,
            )

    @user_bp.delete("/<int:user_id>")
    def delete(user_id: int):
        """
        Deletes a user.
        """
        try:
            user_service.delete(user_id)
            return jsonify({"status": "success", "message": "User deleted successfully"}), 200
        except ValueError as e:
            return jsonify({"status": "error", "message": str(e)}), 404

    return user_bp
