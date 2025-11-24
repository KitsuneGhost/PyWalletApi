from flask import Blueprint

auth_bp = Blueprint("auth_bp", __name__, url_prefix='/auth')

@auth_bp.route("/register", methods=["POST"])
def register():
    pass

@auth_bp.route("/login", methods=["POST"])
def login():
    pass

