from flask import Flask

from app.configs.config import Config
from app.extensions.extensions import db, ma
from app.routes.userRoutes import user_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # initialize extensions
    db.init_app(app)
    ma.init_app(app)

    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()

    return app
