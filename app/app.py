from flask import Flask

from app.configs.config import Config
from app.extensions.extensions import db, ma
from app.models.token_revocation import TokenRevocation

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
from app.auth.password_hasher import PasswordHasher
from app.auth.authService import AuthService

# Domain services
from app.services.userService import UserService
from app.services.walletService import WalletService
from app.services.transactionService import TransactionService

# Route factories
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
        revocations = TokenRevocation()

        # --- repositories ---
        user_repository = UserRepository(user)
        wallet_repository = WalletRepository(wallet)
        transaction_repository = TransactionRepository(transaction)

        # --- auth wiring ---

        # --- domain services ---
        user_service = UserService(user_repository)
        wallet_service = WalletService(wallet_repository, user_repository)
        transaction_service = TransactionService(transaction_repository, user_repository, wallet_repository)

        # --- blueprints ---
        app.register_blueprint(create_user_routes(user_service))
        app.register_blueprint(create_wallet_routes(wallet_service))

        # --- DB bootstrapping (dev only) ---
        db.create_all()

    return app
