from flask import Flask

from app.configs.config import Config
from app.extensions.extensions import db, ma

# Models
from app.models.transaction import Transaction
from app.models.user import User
from app.models.wallet import Wallet

# Repos
from app.repositories.userRepository import UserRepository
from app.repositories.walletRepository import WalletRepository
from app.repositories.transactionRepository import TransactionRepository

# Auth components
from app.auth.token_provider import TokenProvider
from app.auth.password_hasher import PasswordHasherService
from app.auth.revocation_store import RevocationStore
from app.auth.authService import AuthService
from app.auth.decorators import jwt_required

# Domain services
from app.services.userService import UserService
from app.services.walletService import WalletService
from app.services.transactionService import TransactionService

# Route factories
from app.auth.authRoutes import create_auth_routes
from app.routes.userRoutes import create_user_routes
from app.routes.walletRoutes import create_wallet_routes


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # --- extensions ---
    db.init_app(app)
    ma.init_app(app)

    with app.app_context():
        # --- models ---
        user = User()
        wallet = Wallet()
        transaction = Transaction()

        # --- repositories ---
        user_repository = UserRepository(user)
        wallet_repository = WalletRepository(wallet)
        transaction_repository = TransactionRepository(transaction)

        # --- auth wiring ---
        token_provider = TokenProvider(
            secret=app.config["JWT_SECRET"],
            issuer=app.config["JWT_ISSUER"],
            access_minutes=30,
            refresh_days=14,
        )
        revocations = RevocationStore(db.session)      # or RevocationStore(redis_client)
        password_hasher = PasswordHasherService()

        auth_service = AuthService(user_repository, password_hasher, token_provider, revocations)

        # Inject dependencies into decorator (simple DI)
        jwt_required.tokens = token_provider
        jwt_required.revocations = revocations
        jwt_required.users = user_repository

        # --- domain services ---
        user_service = UserService(user_repository)
        wallet_service = WalletService(wallet_repository, user_repository)
        transaction_service = TransactionService(transaction_repository, user_repository, wallet_repository)

        # --- blueprints ---
        app.register_blueprint(create_auth_routes(auth_service, jwt_required))
        app.register_blueprint(create_user_routes(user_service))
        app.register_blueprint(create_wallet_routes(wallet_service))

        # --- DB bootstrapping (dev only) ---
        db.create_all()

    return app
