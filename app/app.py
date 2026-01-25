import os
from datetime import timedelta

from flask import Flask

from app.configs.config import Config
from app.extensions.extensions import db, ma
from dotenv import load_dotenv

# Models
from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import Wallet

# Repos
from app.repositories.userRepository import UserRepository
from app.repositories.walletRepository import WalletRepository
from app.repositories.transactionRepository import TransactionRepository

# Auth components
from app.auth.token_provider import TokenProvider, TokenConfig
from app.models.token_revocation import TokenRevocation
from app.auth.password_hasher import PasswordHasher
from app.auth.decorators import Decorator
from app.auth.authService import AuthService
from app.auth.authRoutes import create_auth_routes

# Domain services
from app.services.userService import UserService
from app.services.walletService import WalletService
from app.services.transactionService import TransactionService

# Route factories
from app.routes.userRoutes import create_user_routes
from app.routes.walletRoutes import create_wallet_routes
from app.util.util import env_int, env_str


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    load_dotenv()

    # --- extensions ---
    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        # --- models ---
        revocations = TokenRevocation()

        # --- repositories ---
        user_repository = UserRepository(User)
        wallet_repository = WalletRepository(Wallet)
        transaction_repository = TransactionRepository(Transaction)

        # --- auth wiring ---
        issuer = os.getenv("JWT_ISSUER")
        secret = os.getenv("JWT_SECRET")
        algorithm = env_str("JWT_ALGORITHM", "HS256")
        access_ttl = env_int("JWT_ACCESS_TTL_MINUTES", 15)
        refresh_ttl = env_int("JWT_REFRESH_TTL_DAYS", 7)

        auth_config = TokenConfig(
            issuer=issuer,
            secret=secret,
            algorithm=algorithm,
            access_ttl=timedelta(access_ttl),
            refresh_ttl=timedelta(refresh_ttl)
        )

        hasher = PasswordHasher()
        token_provider = TokenProvider(auth_config)
        decorator = Decorator(token_provider, user_repository)

        # --- domain services ---
        user_service = UserService(user_repository)
        wallet_service = WalletService(wallet_repository, user_repository)
        transaction_service = TransactionService(transaction_repository, user_repository, wallet_repository)
        auth_service = AuthService(user_repository, hasher, token_provider,   revocations)

        # --- blueprints ---
        app.register_blueprint(create_user_routes(user_service))
        app.register_blueprint(create_wallet_routes(wallet_service))
        app.register_blueprint(create_auth_routes(auth_service, decorator))

        # --- DB bootstrapping (dev only) ---
        db.create_all()

    return app
