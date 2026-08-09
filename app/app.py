from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from app.configs.config import Config
from app.extensions.extensions import db, jwt, ma
from app.routes.userRoutes import user_bp
from app.routes.walletRoutes import wallet_bp
from app.routes.transactionRoutes import transaction_bp


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)

    jwt_secret = app.config.get("JWT_SECRET_KEY")
    if not jwt_secret or len(jwt_secret) < 32 or jwt_secret.startswith("replace-"):
        raise RuntimeError("JWT_SECRET_KEY must be at least 32 random characters")

    # initialize extensions
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    @jwt.token_in_blocklist_loader
    def reject_stale_user(_header, payload):
        from app.models.user import User
        from app.models.tokenSession import TokenSession
        try:
            user = db.session.get(User, int(payload["sub"]))
            session = db.session.get(TokenSession, payload["sid"])
        except (KeyError, TypeError, ValueError):
            return True
        return user is None or session is None or session.is_revoked or user.role != payload.get("role")

    @jwt.unauthorized_loader
    def missing_token(message):
        return jsonify(status="error", message=message), 401

    @jwt.invalid_token_loader
    def invalid_token(message):
        return jsonify(status="error", message=message), 422

    @jwt.expired_token_loader
    def expired_token(_header, _payload):
        return jsonify(status="error", message="Token has expired"), 401

    @jwt.revoked_token_loader
    def revoked_token(_header, _payload):
        return jsonify(status="error", message="Token has been revoked"), 401

    app.register_blueprint(user_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(transaction_bp)

    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.errorhandler(HTTPException)
    def http_error(exc):
        return jsonify(status="error", message=exc.description), exc.code

    @app.errorhandler(Exception)
    def unexpected_error(exc):
        db.session.rollback()
        app.logger.exception("Unhandled API error")
        return jsonify(status="error", message="Internal server error"), 500

    with app.app_context():
        if app.config.get("AUTO_CREATE_DB", True):
            db.create_all()

    return app
