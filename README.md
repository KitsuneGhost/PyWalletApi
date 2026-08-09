# pyWallet API

pyWallet is a secure REST API for managing users, wallets, and monetary transactions. It was built with Flask using a layered architecture and focuses on the parts of financial APIs where correctness matters most: authentication, authorization, decimal-safe balances, atomic operations, immutable history, and session revocation.

> Portfolio project: designed as a complete local application and engineering demonstration, not as a regulated banking or payment product.

## Highlights

- Short-lived JWT access tokens and 30-day refresh tokens
- Database-backed login sessions with immediate logout and token revocation
- Scrypt password hashing and enforced password length
- Resource-level authorization for profiles, wallets, and transaction history
- Atomic withdrawals and transfers with rollback on failure
- Fixed-precision `Decimal` amounts—no floating-point money calculations
- Row locking and deterministic lock order to reduce concurrency hazards
- Database constraints against negative balances and invalid transactions
- Zero-balance wallet archival that preserves historical references
- Paginated wallet and transaction collections
- Marshmallow request validation and consistent JSON error responses
- Security headers, request-size limits, and secure configuration defaults
- Integration tests covering authentication, authorization, revocation, and balance integrity

## Technology

| Area | Technology |
| --- | --- |
| API | Python, Flask |
| Persistence | SQLAlchemy, Flask-SQLAlchemy |
| Validation | Marshmallow |
| Authentication | Flask-JWT-Extended |
| Password storage | Werkzeug scrypt hashes |
| Databases | SQLite for local development; PostgreSQL driver included |
| Migrations | Flask-Migrate / Alembic |
| Tests | Python `unittest`, Flask test client |

## Architecture

The application separates HTTP concerns from business rules and persistence:

```text
Client
  └── Routes       authentication, HTTP status codes, serialization
       └── Services      ownership rules and transaction logic
            └── Repositories   database queries and persistence
                 └── Models         users, wallets, transactions, sessions
```

```text
app/
├── configs/       environment-based configuration
├── dto/           typed data-transfer objects
├── extensions/    SQLAlchemy, Marshmallow, and JWT instances
├── models/        database entities and constraints
├── repositories/  persistence operations
├── routes/        REST endpoints
├── schemas/       request validation and response serialization
└── services/      application and financial business rules
tests/             end-to-end API security tests
```

## Security and financial integrity

Each login creates a server-side token session. Access and refresh tokens share that session identifier, allowing logout to revoke the entire session immediately—including access tokens created through refresh. Tokens are also rejected if their user has been deleted or their role has changed.

Money operations use fixed-precision database numerics and Python decimals. A withdrawal or transfer updates balances and records its transaction in one database commit; any error rolls back the complete operation. Transfers lock wallets in stable ID order, validate ownership, require matching currencies, and reject overdrafts or balance overflow.

The API deliberately provides no public deposit or balance-edit endpoint. Without a verified payment provider, accepting deposits would allow callers to create funds from nothing. Development fixtures or a future trusted payment integration must establish legitimate starting balances.

Wallets with funds cannot be deleted. A zero-balance wallet is archived instead of physically removed, preserving foreign keys and financial history.

## Getting started

### Requirements

- Python 3.11 or newer
- SQLite, or a PostgreSQL instance

### Installation

```bash
git clone https://github.com/KitsuneGhost/PyWalletApi.git
cd pyWalletApi

python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

Put the generated value in `.env` as `JWT_SECRET_KEY`, then start the API:

```bash
python run.py
```

The development server listens on `http://127.0.0.1:8080`.

### Configuration

```dotenv
DATABASE_URL=sqlite:///pywallet.db
JWT_SECRET_KEY=your-generated-random-secret
```

`JWT_SECRET_KEY` is mandatory, must contain at least 32 characters, and must never be committed. PostgreSQL connection strings can be supplied through `DATABASE_URL`:

```dotenv
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/pywallet
```

## API workflow

### 1. Register

```bash
curl -X POST http://127.0.0.1:8080/users/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "demo_user",
    "email": "demo@example.com",
    "password": "a long unique passphrase"
  }'
```

Public registration always creates a normal `USER`; callers cannot assign themselves administrator privileges.

### 2. Log in

```bash
curl -X POST http://127.0.0.1:8080/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "demo@example.com",
    "password": "a long unique passphrase"
  }'
```

The response contains an `access_token` and `refresh_token`. Send the access token as a bearer token:

```bash
curl http://127.0.0.1:8080/users/me \
  -H "Authorization: Bearer <access_token>"
```

### 3. Create a wallet

```bash
curl -X POST http://127.0.0.1:8080/wallets/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"name": "Daily expenses", "currency": "EUR"}'
```

### 4. Transfer funds

```bash
curl -X POST http://127.0.0.1:8080/transactions/wallets/1/transfer \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"to_wallet_id": 2, "amount": "25.50"}'
```

### 5. Refresh or revoke the session

```bash
curl -X POST http://127.0.0.1:8080/users/refresh \
  -H "Authorization: Bearer <refresh_token>"

curl -X POST http://127.0.0.1:8080/users/logout \
  -H "Authorization: Bearer <access_or_refresh_token>"
```

Logout revokes both tokens belonging to that login session.

## Endpoint summary

### Users and authentication

| Method | Path | Access | Description |
| --- | --- | --- | --- |
| `POST` | `/users/register` | Public | Register a user |
| `POST` | `/users/login` | Public | Create a token session |
| `POST` | `/users/refresh` | Refresh token | Issue a new access token |
| `POST` | `/users/logout` | Any valid token | Revoke the login session |
| `GET` | `/users/me` | User | Read the current profile |
| `GET` | `/users/{id}` | Owner/admin | Read a profile |
| `PATCH` | `/users/{id}` | Owner/admin | Update a profile |
| `DELETE` | `/users/{id}` | Owner/admin | Delete a profile |
| `GET` | `/users/` | Admin | List users |

### Wallets

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/wallets/?page=1&per_page=20` | List owned active wallets |
| `POST` | `/wallets/` | Create a zero-balance wallet |
| `GET` | `/wallets/{id}` | Read an owned wallet |
| `PATCH` | `/wallets/{id}` | Rename an owned wallet |
| `DELETE` | `/wallets/{id}` | Archive an owned zero-balance wallet |

### Transactions

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/transactions/?page=1&per_page=20` | Paginated transaction history |
| `POST` | `/transactions/wallets/{id}/withdraw` | Withdraw from an owned wallet |
| `POST` | `/transactions/wallets/{id}/transfer` | Transfer to an active same-currency wallet |

Collection endpoints accept positive `page` and `per_page` values. Page size is capped at 100.

## Response format

Successful responses use a consistent envelope:

```json
{
  "status": "success",
  "data": {}
}
```

Validation and application errors are returned as JSON:

```json
{
  "status": "error",
  "message": "Insufficient funds"
}
```

Unexpected exceptions are logged server-side while clients receive a generic message, avoiding internal detail leakage.

## Tests

Run the integration suite with:

```bash
python -m unittest discover -v
```

The tests exercise:

- unauthenticated request rejection
- protected wallet access
- prevention of direct balance assignment
- overdraft rollback and unchanged balances
- preservation of history after wallet archival
- pagination behavior
- prevention of role escalation during registration
- isolation between different users' wallets
- access-token refresh
- full-session revocation after logout

The pinned dependencies have also been checked with `pip-audit`.

## Design boundaries

This repository intentionally stops short of pretending to be a real payment platform. A production financial service would additionally require a verified funding/payout provider, idempotency keys, rate limiting, audit infrastructure, regulatory controls, reconciliation, observability, encrypted backups, managed secrets, TLS, and a production WSGI deployment.

For an existing local database created by an earlier version, recreate it or generate an Alembic migration. `db.create_all()` creates missing tables but does not add new columns to existing ones.
